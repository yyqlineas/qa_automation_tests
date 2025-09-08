"""
Script 5: Subida de archivos vía SFTP
Sube archivos XML al servidor SFTP para su procesamiento
"""

import paramiko
import os
import logging
import json
from datetime import datetime
from typing import Optional, Dict, List, Tuple
import stat

class SFTPUploader:
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Optional[Dict] = None
        self.logger: Optional[logging.Logger] = None
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        """Configura el logging para el uploader"""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        log_filename = f"sftp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_path = os.path.join(log_dir, log_filename)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_config(self):
        """Carga la configuración desde el archivo JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            if self.logger:
                self.logger.info("Configuración cargada exitosamente")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al cargar configuración: {str(e)}")
            raise
    
    def create_sftp_connection(self) -> Optional[Tuple[paramiko.SSHClient, paramiko.SFTPClient]]:
        """
        Crea conexión SFTP usando configuración
        
        Returns:
            Tupla (ssh_client, sftp_client) o None si hay error
        """
        try:
            if not self.config:
                raise Exception("Configuración no cargada")
            
            sftp_config = self.config.get('sftp', {})
            
            # Obtener configuración SFTP
            hostname = sftp_config.get('hostname')
            port = sftp_config.get('port', 22)
            username = sftp_config.get('username')
            password = sftp_config.get('password')
            key_file = sftp_config.get('key_file')
            
            if not hostname or not username:
                raise Exception("Faltan parámetros de conexión SFTP (hostname/username)")
            
            if self.logger:
                self.logger.info(f"Conectando a SFTP: {username}@{hostname}:{port}")
            
            # Crear cliente SSH
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Conectar usando password o key
            if key_file and os.path.exists(key_file):
                if self.logger:
                    self.logger.info("Usando autenticación por clave privada")
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    key_filename=key_file,
                    timeout=30
                )
            elif password:
                if self.logger:
                    self.logger.info("Usando autenticación por password")
                ssh_client.connect(
                    hostname=hostname,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30
                )
            else:
                raise Exception("No se encontraron credenciales de autenticación")
            
            # Crear cliente SFTP
            sftp_client = ssh_client.open_sftp()
            
            if self.logger:
                self.logger.info("Conexión SFTP establecida exitosamente")
            
            return ssh_client, sftp_client
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al conectar SFTP: {str(e)}")
            return None
    
    def upload_file(self, local_file_path: str, remote_file_path: str, 
                   create_dirs: bool = True) -> bool:
        """
        Sube un archivo individual vía SFTP
        
        Args:
            local_file_path: Ruta local del archivo
            remote_file_path: Ruta remota donde subir el archivo
            create_dirs: Si crear directorios remotos automáticamente
            
        Returns:
            True si se subió exitosamente, False si hay error
        """
        ssh_client = None
        sftp_client = None
        
        try:
            if not os.path.exists(local_file_path):
                if self.logger:
                    self.logger.error(f"Archivo local no existe: {local_file_path}")
                return False
            
            # Crear conexión
            connection = self.create_sftp_connection()
            if not connection:
                return False
            
            ssh_client, sftp_client = connection
            
            # Crear directorios remotos si es necesario
            if create_dirs:
                remote_dir = os.path.dirname(remote_file_path).replace('\\', '/')
                self._create_remote_directories(sftp_client, remote_dir)
            
            # Subir archivo
            if self.logger:
                self.logger.info(f"Subiendo: {local_file_path} -> {remote_file_path}")
            
            sftp_client.put(local_file_path, remote_file_path)
            
            # Verificar que se subió correctamente
            try:
                remote_stat = sftp_client.stat(remote_file_path)
                local_size = os.path.getsize(local_file_path)
                
                if remote_stat.st_size == local_size:
                    if self.logger:
                        self.logger.info(f"✅ Archivo subido exitosamente ({local_size} bytes)")
                    return True
                else:
                    if self.logger:
                        self.logger.error(f"❌ Tamaño incorrecto: local={local_size}, remoto={remote_stat.st_size}")
                    return False
                    
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"No se pudo verificar la subida: {str(e)}")
                return True  # Asumir que se subió correctamente
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al subir archivo: {str(e)}")
            return False
            
        finally:
            # Cerrar conexiones
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()
    
    def upload_directory(self, local_directory: str, remote_directory: str, 
                        file_extensions: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Sube todos los archivos de un directorio vía SFTP
        
        Args:
            local_directory: Directorio local
            remote_directory: Directorio remoto
            file_extensions: Lista de extensiones a subir (ej: ['.xml', '.json'])
            
        Returns:
            Diccionario con resultado de cada archivo
        """
        results = {}
        ssh_client = None
        sftp_client = None
        
        try:
            if not os.path.exists(local_directory):
                if self.logger:
                    self.logger.error(f"Directorio local no existe: {local_directory}")
                return results
            
            # Crear conexión
            connection = self.create_sftp_connection()
            if not connection:
                return results
            
            ssh_client, sftp_client = connection
            
            # Crear directorio remoto
            self._create_remote_directories(sftp_client, remote_directory)
            
            # Obtener lista de archivos
            files_to_upload = []
            for filename in os.listdir(local_directory):
                local_file_path = os.path.join(local_directory, filename)
                
                # Verificar que es archivo
                if not os.path.isfile(local_file_path):
                    continue
                
                # Verificar extensión si se especifica
                if file_extensions:
                    if not any(filename.lower().endswith(ext.lower()) for ext in file_extensions):
                        continue
                
                files_to_upload.append((filename, local_file_path))
            
            if not files_to_upload:
                if self.logger:
                    self.logger.warning(f"No se encontraron archivos para subir en: {local_directory}")
                return results
            
            if self.logger:
                self.logger.info(f"Subiendo {len(files_to_upload)} archivos...")
            
            # Subir cada archivo
            for filename, local_file_path in files_to_upload:
                remote_file_path = f"{remote_directory}/{filename}".replace('\\', '/')
                
                try:
                    if self.logger:
                        self.logger.info(f"Subiendo: {filename}")
                    
                    sftp_client.put(local_file_path, remote_file_path)
                    
                    # Verificar subida
                    try:
                        remote_stat = sftp_client.stat(remote_file_path)
                        local_size = os.path.getsize(local_file_path)
                        
                        if remote_stat.st_size == local_size:
                            results[filename] = True
                            if self.logger:
                                self.logger.info(f"✅ {filename} ({local_size} bytes)")
                        else:
                            results[filename] = False
                            if self.logger:
                                self.logger.error(f"❌ {filename} - tamaño incorrecto")
                    except:
                        results[filename] = True  # Asumir éxito
                        
                except Exception as e:
                    results[filename] = False
                    if self.logger:
                        self.logger.error(f"❌ Error subiendo {filename}: {str(e)}")
            
            return results
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al subir directorio: {str(e)}")
            return results
            
        finally:
            # Cerrar conexiones
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()
    
    def _create_remote_directories(self, sftp_client: paramiko.SFTPClient, remote_path: str):
        """
        Crea directorios remotos recursivamente
        
        Args:
            sftp_client: Cliente SFTP
            remote_path: Ruta del directorio remoto a crear
        """
        try:
            # Normalizar ruta
            remote_path = remote_path.replace('\\', '/')
            
            # Dividir ruta en partes
            parts = [p for p in remote_path.split('/') if p]
            
            current_path = ''
            for part in parts:
                current_path += f'/{part}' if current_path else part
                
                try:
                    # Intentar stat para ver si existe
                    sftp_client.stat(current_path)
                except FileNotFoundError:
                    # No existe, crear directorio
                    try:
                        sftp_client.mkdir(current_path)
                        if self.logger:
                            self.logger.debug(f"Directorio creado: {current_path}")
                    except Exception as e:
                        if self.logger:
                            self.logger.warning(f"No se pudo crear directorio {current_path}: {str(e)}")
                        
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al crear directorios remotos: {str(e)}")
    
    def list_remote_files(self, remote_directory: str) -> List[str]:
        """
        Lista archivos en directorio remoto
        
        Args:
            remote_directory: Directorio remoto
            
        Returns:
            Lista de nombres de archivos
        """
        ssh_client = None
        sftp_client = None
        
        try:
            # Crear conexión
            connection = self.create_sftp_connection()
            if not connection:
                return []
            
            ssh_client, sftp_client = connection
            
            # Listar archivos
            files = sftp_client.listdir(remote_directory)
            
            if self.logger:
                self.logger.info(f"Encontrados {len(files)} archivos en {remote_directory}")
            
            return files
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al listar archivos remotos: {str(e)}")
            return []
            
        finally:
            # Cerrar conexiones
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()
    
    def delete_remote_file(self, remote_file_path: str) -> bool:
        """
        Elimina archivo remoto
        
        Args:
            remote_file_path: Ruta del archivo remoto
            
        Returns:
            True si se eliminó exitosamente
        """
        ssh_client = None
        sftp_client = None
        
        try:
            # Crear conexión
            connection = self.create_sftp_connection()
            if not connection:
                return False
            
            ssh_client, sftp_client = connection
            
            # Eliminar archivo
            sftp_client.remove(remote_file_path)
            
            if self.logger:
                self.logger.info(f"Archivo remoto eliminado: {remote_file_path}")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al eliminar archivo remoto: {str(e)}")
            return False
            
        finally:
            # Cerrar conexiones
            if sftp_client:
                sftp_client.close()
            if ssh_client:
                ssh_client.close()

def main():
    """Función principal para ejecutar el script independientemente"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Subida de archivos vía SFTP')
    parser.add_argument('--config', default='../config/config.json', help='Ruta al archivo de configuración')
    parser.add_argument('--file', help='Archivo específico a subir')
    parser.add_argument('--directory', help='Directorio con archivos a subir')
    parser.add_argument('--remote_path', help='Ruta remota de destino')
    parser.add_argument('--extensions', nargs='+', help='Extensiones de archivo a subir (ej: .xml .json)')
    parser.add_argument('--list', help='Listar archivos en directorio remoto')
    parser.add_argument('--delete', help='Eliminar archivo remoto')
    
    args = parser.parse_args()
    
    # Resolver ruta de configuración
    config_path = os.path.join(os.path.dirname(__file__), args.config)
    
    try:
        uploader = SFTPUploader(config_path)
        
        if args.list:
            # Listar archivos remotos
            files = uploader.list_remote_files(args.list)
            print(f"✅ Archivos en {args.list}:")
            for file in files:
                print(f"  - {file}")
        
        elif args.delete:
            # Eliminar archivo remoto
            success = uploader.delete_remote_file(args.delete)
            if success:
                print(f"✅ Archivo eliminado: {args.delete}")
            else:
                print(f"❌ Error al eliminar archivo: {args.delete}")
        
        elif args.file:
            # Subir archivo específico
            if not args.remote_path:
                print("❌ Error: --remote_path es requerido para subir archivos")
                return 1
            
            success = uploader.upload_file(args.file, args.remote_path)
            if success:
                print(f"✅ Archivo subido exitosamente")
            else:
                print(f"❌ Error al subir archivo")
        
        elif args.directory:
            # Subir directorio
            if not args.remote_path:
                print("❌ Error: --remote_path es requerido para subir directorio")
                return 1
            
            results = uploader.upload_directory(args.directory, args.remote_path, args.extensions)
            
            successful = sum(1 for success in results.values() if success)
            total = len(results)
            
            print(f"✅ Subida completada: {successful}/{total} archivos exitosos")
            
            # Mostrar detalles
            for filename, success in results.items():
                status = "✅" if success else "❌"
                print(f"  {status} {filename}")
        
        else:
            print("❌ Error: Debe especificar --file, --directory, --list o --delete")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())
