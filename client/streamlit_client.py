import streamlit as st
import requests
import time
import os

# -------------------
# 1. 全局设置与状态存储
# -------------------
BASE_URL = "http://localhost:20926"

# 若不存在则初始化，用于记录所有文件的状态
if "file_status" not in st.session_state:
    st.session_state.file_status = []


# -------------------
# 2. 工具函数
# -------------------

def poll_jobs():
    """
    轮询未完成的任务，更新状态为 completed / failed / processing
    每次 Streamlit 刷新时调用一次。
    """
    for item in st.session_state.file_status:
        if item["status"] not in ["completed", "failed"]:
            try:
                response = requests.get(f"{BASE_URL}/api/jobs/{item['job_id']}")
                if response.status_code == 200:
                    job_data = response.json()
                    job_status = job_data.get("status", "unknown")
                    item["status"] = job_status
                else:
                    item["status"] = "failed"
            except requests.RequestException:
                item["status"] = "failed"


def upload_file(file, pdf_mode):
    """
    上传单个文件到后端，创建任务。
    不在此处阻塞等待结果，而是将任务信息记录到 st.session_state.file_status
    """
    files = {"file": file}
    data = {"pdf_mode": pdf_mode}
    try:
        response = requests.post(f"{BASE_URL}/api/jobs", files=files, data=data)
        if response.status_code == 202:
            job_id = response.json().get("job_id")
            st.session_state.file_status.append({
                "name": file.name,
                "status": "processing",
                "job_id": job_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": file.type
            })
            st.success(f"文件 `{file.name}` 上传成功，已加入任务队列。")
        else:
            st.error(f"文件 `{file.name}` 上传失败: {response.text}")
    except requests.RequestException as e:
        st.error(f"网络异常：{e}")


def upload_url(url, pdf_mode):
    """
    上传单个 URL 到后端，创建任务。
    """
    data = {"url": url, "pdf_mode": pdf_mode}
    try:
        response = requests.post(f"{BASE_URL}/api/jobs/url", json=data)
        if response.status_code == 202:
            job_id = response.json().get("job_id")
            st.session_state.file_status.append({
                "name": url.split("/")[-1],  # 取 URL 最后的部分作为文件名
                "status": "processing",
                "job_id": job_id,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": "URL"
            })
            st.success(f"URL `{url}` 提交成功，已加入任务队列。")
        else:
            st.error(f"URL `{url}` 上传失败: {response.text}")
    except requests.RequestException as e:
        st.error(f"网络异常：{e}")


def show_file_entry(file):
    """
    在右侧文件列表中渲染每个文件条目。
    """
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

    with col1:
        st.markdown(f"**{file['name']}**")

    with col2:
        st.markdown(f"{file['timestamp']}")

    with col3:
        status = file["status"]
        if status == "completed":
            status_icon = "✅"
        elif status == "failed":
            status_icon = "❌"
        else:
            status_icon = "⏳"
        st.markdown(f"{status_icon} {status}")

    with col4:
        # 如果已完成，提供下载
        if file["status"] == "completed":
            try:
                result_response = requests.get(f"{BASE_URL}/api/jobs/{file['job_id']}/result")
                if result_response.status_code == 200:
                    st.download_button(
                        label="下载",
                        data=result_response.content,
                        file_name=f"{file['name']}.md",
                        mime="text/markdown"
                    )
                else:
                    st.error("下载失败")
            except requests.RequestException as e:
                st.error(f"下载异常：{e}")


# -------------------
# 3. 主函数
# -------------------
def main():
    st.set_page_config(page_title="Markify", layout="wide")

    # 页面标题与说明
    st.title("Markify - 文档处理")
    st.markdown("在左侧上传文件或提交 URL，右侧实时查看进度并下载结果。")

    # 轮询已存在任务的状态
    poll_jobs()

    # 主体布局：左侧上传，右侧列表
    left_col, right_col = st.columns([2, 3], gap="large")

    with left_col:
        st.subheader("上传设置")
        pdf_mode = st.selectbox("选择 PDF 处理模式", ["simple", "advanced", "cloud"])

        # 本地文件上传
        uploaded_files = st.file_uploader(
            "选择文件（PDF、Word、PPT、Audio、HTML、CSV、JSON、XML、ZIP等）",
            type=None,  # ["pdf", "docx", "ppt"],
            accept_multiple_files=True
        )
        if uploaded_files and st.button("上传文件"):
            for file in uploaded_files:
                upload_file(file, pdf_mode)

        # URL 上传
        st.subheader("URL 上传")
        file_urls = st.text_area("请输入文件 URL（每行一个）")
        if file_urls and st.button("提交 URL"):
            for url in file_urls.strip().split("\n"):
                if url:
                    upload_url(url.strip(), pdf_mode)

        # 结果存储位置
        st.markdown(f"**解析结果存储路径**：`{os.path.expanduser('~')}/MinerU`")

    with right_col:
        st.subheader("文件列表")

        # 手动刷新按钮
        if st.button("刷新列表"):
            st.experimental_rerun()

        if len(st.session_state.file_status) == 0:
            st.info("暂无文件，请上传后查看。")
        else:
            for item in st.session_state.file_status:
                show_file_entry(item)


if __name__ == "__main__":
    main()
