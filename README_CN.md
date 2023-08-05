# jellyfin-transubtitle

这是一个用于自动将Jellyfin媒体服务器中的ASS格式字幕翻译成其他语言的Python脚本。它使用百度文本翻译API进行翻译。

## 如何使用

1. 安装 Docker（包括 Docker Compose）。
2. 复制 ```.env.example``` 文件并将其命名为 ```.env```，然后进行编辑。
3. 执行 ```docker-compose up``` 命令来启动容器（如果要作为守护进程运行，则添加 ```-d``` 选项）。

## 参数说明

以下是可以定义的参数及其作用：

- `USER_NAME`：要翻译字幕的Jellyfin用户的用户名。
- `BASE_URI`：Jellyfin服务器的基本URL。
- `API_TOKEN`：访问Jellyfin服务器的API令牌。
- `JELLYFIN_TARGET_LANG`：要翻译成的[目标语言](doc/language.md)。
- `SCAN_INTERVAL`：脚本扫描新媒体项目的间隔时间（以秒为单位）。

在运行脚本之前，请确保正确设置环境变量。

### 百度文本翻译API

该脚本使用百度文本翻译API。这需要设置以下百度API凭据作为环境变量：

- `BAIDU_APP_ID`：百度文本翻译API的App ID。
- `BAIDU_APP_KEY`：百度文本翻译API的App Key。
- `BAIDU_TARGET_LANG`：使用百度文本翻译API进行翻译的[目标语言](http://api.fanyi.baidu.com/doc/21)。

## 其他说明

该脚本执行以下任务：

1. 使用`jellyfin('Users')`函数从Jellyfin服务器加载用户信息，并根据提供的用户名提取用户ID。
2. 定义一个`scan`函数，递归扫描用户的媒体库，并为每个媒体项目调用提供的回调函数。
3. 定义一个`translate_ass`函数，使用百度文本翻译API翻译ASS格式字幕文件的内容。
4. 定义一个`translate_subtitle`函数，检查媒体项目是否具有ASS格式字幕，并在目标语言尚不可用时进行翻译。
5. 进入一个循环，不断扫描新的媒体项目，并使用`scan`和`translate_subtitle`函数翻译它们的字幕。
6. 通过键盘中断（Ctrl+C）来优雅地停止脚本的循环。
