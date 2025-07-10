
class HtmlTemplates:
    """Central place for raw HTML, CSS content."""

    @staticmethod
    def error_bar():
        return """
        <div style='border: 1px solid orange; width: 100%; padding: 8px; color: orange; text-align: center; border-radius: 5px;'>
            ⚠️ No file selected. Please select a file to upload.
        </div>
        """

    @staticmethod
    def progress_bar(percent: int, current: int, total: int):
        return f"""
        <div style='border: 1px solid #ccc; width: 100%; height: 20px; position: relative; border-radius: 5px; overflow: hidden;'>
            <div style='background-color: #4caf50; width: {percent}%; height: 100%; transition: width 0.5s;'></div>
        </div>
        <p style='text-align: center;'>Uploaded {current} / {total} files ({percent}%)</p>
        """

    @staticmethod
    def css():
        return """
            #title {
                margin-top: 8px;
                text-align: center;
                background-color: #2596be; /* blue */
                color: white;
                padding: 12px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 24px;
            }


            #upload-btn {
                background-color: #e28743;      /* orange */
                color: white;                   /* Text color */
                border-radius: 6px;             /* Rounded corners */
                padding: 10px 16px;
                font-weight: bold;
                font-size: 18px;
            }

            #upload-btn:hover {
                background-color: #cb7a3c;      /* Darker on hover */
            }
        """

