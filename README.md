# Markify

✨ **将文件转换为 Markdown，助力 RAG 与 LLM 更好地理解内容！** ✨  

🚀 **基于 Markitdown 和 MinerU**，不仅支持多种格式转换（如 Markitdown），还可借助 MinerU 提供高质量的 **PDF 解析** 功能。  

📡 **支持 API 接口 & Streamlit 页面**，随时随地轻松使用！  

📖 **当前支持的文件格式，包括但不限于以下格式**：
- PDF
- PPT
- Word
- Excel
- Images
- Audio
- HTML
- CSV, JSON和XML
- ZIP压缩文件

📖 **当前支持的 PDF 解析模式**：  
- ⚡ **简单模式**（使用 pdfminer，解析速度快）  
- 🏆 **高级模式**（使用 MinerU，结合模型解析 PDF，效果更优但速度较慢）  
- ☁️ **云端模式**（开发中，敬请期待！）  

📂 **高效转换，轻松集成，助力你的 LLM 处理文档！** 💡

![alt text](assets/streamlint ui.png)
```shell
streamlit run ./client/streamlit_client.py
```

## API
FastAPI自带API文档 http://127.0.0.1:20926/docs
### 上传文件，创建任务
请求
```shell
curl -X 'POST' \
  'http://127.0.0.1:20926/api/jobs' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@CoA.pdf;type=application/pdf' \
  -F 'pdf_mode=advanced'
```
响应
```json
{
  "job_id": "29bbad6b-c167-41f0-8a29-99551c499263"
}
```
### 查询任务状态
请求
```shell
curl -X 'GET' \
  'http://127.0.0.1:20926/api/jobs/29bbad6b-c167-41f0-8a29-99551c499263' \
  -H 'accept: application/json'
```
响应
```json
{
  "job_id": "29bbad6b-c167-41f0-8a29-99551c499263",
  "status": "completed",
  "filename": "CoA.pdf",
  "params": {
    "pdf_mode": "advanced"
  },
  "error": null
}
```
### 下载markdown文件
请求
```shell
curl -X 'GET' \
  'http://127.0.0.1:20926/api/jobs/29bbad6b-c167-41f0-8a29-99551c499263/result' \
  -H 'accept: application/json'
```
响应
文件


## Docker部署
```shell
docker pull wsjcuhk/markify:0.0.1
docker run -d -p 20926:20926 wsjcuhk/markify:0.0.1
```


## TODO
- 优化Mineru中输出的图像地址为本机地址
- 添加云端解析模式
