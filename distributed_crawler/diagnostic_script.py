# diagnostic_script.py  
import sys  
import os  
import traceback  
import logging  

# 配置日志，确保输出到文件  
logging.basicConfig(  
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s: %(message)s',  
    filename='diagnostic_log.txt',  
    filemode='w'  
)  

def comprehensive_diagnostic():  
    # 同时打印到控制台和文件  
    def log_and_print(message):  
        print(message)  
        logging.info(message)  

    try:  
        log_and_print("=" * 50)  
        log_and_print("🔍 项目环境诊断报告")  
        log_and_print("=" * 50)  

        # Python 运行时信息  
        log_and_print("\n[Python 运行时信息]")  
        log_and_print(f"Python 版本: {sys.version}")  
        log_and_print(f"Python 可执行文件: {sys.executable}")  
        
        # 当前工作目录和 Python 路径  
        current_dir = os.getcwd()  
        log_and_print(f"\n[当前工作目录] {current_dir}")  
        
        log_and_print("\n[Python 搜索路径]")  
        for path in sys.path:  
            log_and_print(path)  

        # 目录结构检查  
        log_and_print("\n[目录结构检查]")  
        critical_dirs = [  
            'crawler',   
            'crawler/core',   
            'crawler/config',   
            'tests'  
        ]  

        for dir_path in critical_dirs:  
            full_path = os.path.join(current_dir, dir_path)  
            if os.path.exists(full_path):  
                log_and_print(f"✅ 目录存在: {full_path}")  
            else:  
                log_and_print(f"❌ 目录缺失: {full_path}")  

        # 模块导入诊断  
        log_and_print("\n[模块导入诊断]")  
        modules_to_check = [  
            'crawler.core.url_manager',   
            'crawler.core.data_crawler',   
            'crawler.config.settings'  
        ]  

        for module_name in modules_to_check:  
            try:  
                # 使用 importlib 替代 __import__  
                import importlib  
                module = importlib.import_module(module_name)  
                log_and_print(f"✅ 成功导入: {module_name}")  
                log_and_print(f"模块路径: {module.__file__}")  
            except ImportError as e:  
                log_and_print(f"❌ 导入失败: {module_name}")  
                log_and_print(str(e))  
                logging.error(traceback.format_exc())  

        # 关键文件检查  
        log_and_print("\n[关键文件检查]")  
        key_files = [  
            'crawler/__init__.py',  
            'crawler/core/__init__.py',  
            'crawler/config/__init__.py',  
            'tests/__init__.py'  
        ]  

        for file_path in key_files:  
            full_path = os.path.join(current_dir, file_path)  
            if os.path.exists(full_path):  
                log_and_print(f"✅ 文件存在: {full_path}")  
                # 额外检查文件内容  
                with open(full_path, 'r') as f:  
                    content = f.read().strip()  
                    log_and_print(f"文件内容: {'空文件' if not content else '非空'}")  
            else:  
                log_and_print(f"❌ 文件缺失: {full_path}")  

        log_and_print("\n诊断完成！")  

    except Exception as e:  
        log_and_print(f"❌ 诊断过程中发生错误: {e}")  
        logging.error(traceback.format_exc())  

def main():  
    comprehensive_diagnostic()  

if __name__ == "__main__":  
    main()