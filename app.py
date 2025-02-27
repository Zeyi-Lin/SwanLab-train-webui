import gradio as gr
import yaml
import subprocess
import os
import sys

def load_config(config_path="config.yaml"):
    """加载配置文件"""
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        return {"error": f"加载配置文件失败: {str(e)}"}

def save_config(config, config_path="config.yaml"):
    """保存配置到文件"""
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_stzyle=False, allow_unicode=True)
        return True
    except Exception as e:
        return False

def flatten_config(config, parent_key="", sep="."):
    """将嵌套的配置扁平化为一级键值对"""
    items = []
    for k, v in config.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_config(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def unflatten_config(flat_config, sep="."):
    """将扁平化的配置恢复为嵌套结构"""
    result = {}
    for key, value in flat_config.items():
        parts = key.split(sep)
        d = result
        for part in parts[:-1]:
            if part not in d:
                d[part] = {}
            d = d[part]
        d[parts[-1]] = value
    return result

def create_ui_components(config):
    """根据配置创建UI组件"""
    flat_config = flatten_config(config)
    components = {}
    inputs = []
    
    for key, value in flat_config.items():
        if isinstance(value, bool):
            component = gr.Checkbox(value=value, label=key)
        elif isinstance(value, int):
            component = gr.Number(value=value, label=key, precision=0)
        elif isinstance(value, float):
            component = gr.Number(value=value, label=key)
        elif isinstance(value, str):
            component = gr.Textbox(value=value, label=key)
        elif isinstance(value, list):
            component = gr.Textbox(value=str(value), label=f"{key} (列表格式)")
        else:
            component = gr.Textbox(value=str(value), label=key)
        
        components[key] = component
        inputs.append(component)
    
    return components, inputs

def update_config_from_ui(components, config_path="config.yaml"):
    """从UI组件更新配置"""
    flat_config = {}
    
    for key, component in components.items():
        value = component.value
        # 处理列表类型
        if key.endswith(" (列表格式)"):
            key = key.replace(" (列表格式)", "")
            try:
                value = eval(value)  # 将字符串转换回列表
            except:
                pass
        flat_config[key] = value
    
    config = unflatten_config(flat_config)
    save_success = save_config(config, config_path)
    return config, save_success

def start_training(train_script="train.py", components=None, config_path="config.yaml"):
    """启动训练脚本"""
    if components:
        config, save_success = update_config_from_ui(components, config_path)
        if not save_success:
            return "配置保存失败，无法启动训练"
    
    try:
        # 使用subprocess启动训练脚本
        process = subprocess.Popen(
            [sys.executable, train_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        output = []
        for line in process.stdout:
            output.append(line.strip())
            if len(output) > 100:  # 限制输出行数
                output.pop(0)
        
        process.wait()
        return "\n".join(output) if output else "训练完成，无输出"
    except Exception as e:
        return f"启动训练失败: {str(e)}"

def main():
    config = load_config()
    if "error" in config:
        print(config["error"])
        return
    
    components, inputs = create_ui_components(config)
    
    with gr.Blocks(title="SwanLab训练控制台") as app:
        gr.Markdown("# SwanLab 训练参数配置")
        
        with gr.Tabs():
            with gr.TabItem("参数配置"):
                for input_component in inputs:
                    input_component.render()
                
                with gr.Row():
                    save_btn = gr.Button("保存配置")
                    train_btn = gr.Button("开始训练", variant="primary")
                
                result = gr.Textbox(label="操作结果")
            
            with gr.TabItem("训练日志"):
                log_output = gr.Textbox(label="训练输出", lines=20)
                refresh_btn = gr.Button("刷新日志")
        
        save_btn.click(
            lambda: update_config_from_ui(components)[1],
            outputs=result
        )
        
        train_btn.click(
            lambda: start_training(components=components),
            outputs=log_output
        )
        
        refresh_btn.click(
            lambda: "日志刷新功能待实现",
            outputs=log_output
        )
    
    app.launch()

if __name__ == "__main__":
    main()
