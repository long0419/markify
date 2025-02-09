import streamlit as st
import requests
import time

# 后端 API 的基础 URL
BASE_URL = "http://localhost:20926"

def main():
    st.title("PDF 转 Markdown")

    # 文件上传组件
    uploaded_file = st.file_uploader("选择一个 PDF 文件", type=["pdf"])

    if uploaded_file is not None:
        # 上传文件按钮
        if st.button("上传文件"):
            # 准备请求数据
            files = {"file": uploaded_file}
            data = {"pdf_mode": "simple"}

            try:
                # 发送 POST 请求到后端的 /api/jobs 端点
                response = requests.post(f"{BASE_URL}/api/jobs", files=files, data=data)

                if response.status_code == 202:
                    job_id = response.json().get("job_id")
                    st.info(f"任务已启动，任务 ID: {job_id}")

                    # 轮询任务状态
                    while True:
                        status_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
                        if status_response.status_code == 200:
                            job_status = status_response.json().get("status")
                            if job_status == "completed":
                                st.success("任务已完成，点击下面的链接下载结果。")
                                # 下载结果文件
                                result_response = requests.get(f"{BASE_URL}/api/jobs/{job_id}/result")
                                if result_response.status_code == 200:
                                    st.download_button(
                                        label="下载 Markdown 文件",
                                        data=result_response.content,
                                        file_name=f"{uploaded_file.name}.md",
                                        mime="text/markdown"
                                    )
                                break
                            elif job_status == "failed":
                                error_message = status_response.json().get("error")
                                st.error(f"任务失败: {error_message}")
                                break
                            else:
                                st.info(f"任务状态: {job_status}，请稍候...")
                                time.sleep(2)  # 每 2 秒检查一次状态
                        else:
                            st.error(f"获取任务状态失败: {status_response.text}")
                            break
                else:
                    st.error(f"文件上传失败: {response.text}")
            except requests.RequestException as e:
                st.error(f"请求出错: {e}")

if __name__ == "__main__":
    main()
