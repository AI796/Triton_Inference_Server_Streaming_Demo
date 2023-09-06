# Triton_Inference_Server_Streaming_Demo

Streaming文件夹为下图Triton Inference Server中红色模块示例代码，未经测试，只是显示一下推流在triton部署中的逻辑。
对于triton部署的推流模块，不要放在main.py的sub_module中，因为会导致主线程阻塞，无法完成后续推理任务。相应的，应该放在类似ensemble model中，因为ensemble可以异步调用，每个模块可以独立工作节约资源。
运行结果应该发送至流媒体服务器以释放triton资源，否则会造成推理服务器的显存浪费。

本人是ffmpeg小白，从来没使用过，相关推流代码可能无法运行，本样例仅显示triton业务逻辑，见谅！欢迎大佬帮忙修正代码。

![Image text](https://github.com/AI796/Triton_Inference_Server_Streaming_Demo/blob/main/pic01.png)

## 测试用轻量化hls推流方案，免流媒体服务器安装

与triton的配合见下图

![Image text](https://github.com/AI796/Triton_Inference_Server_Streaming_Demo/blob/main/m3u8looper/pipeline_demo.png)https://github.com/AI796/Triton_Inference_Server_Streaming_Demo/blob/main/m3u8looper/pipeline_demo.png)
