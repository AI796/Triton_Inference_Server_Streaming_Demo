##############################################################################################
# 以下为Triton环境外调试成功的代码，直接贴在文件头，不用合并进TritonPythonModel类，版本更新时重贴一下即可 #
################################################################################################
import os
import numpy as np
import ffmpeg

def streaming(images_batch,audio,streaming_server_url):
    fps=25
    _,height,width,_=images_batch.shape # 256,256
    
    # 下面ffmpeg代码未经测试，本人属于ffmpeg小白，可能有bug！音频也没有合并进来，求大佬提供样例
    process=(
        ffmpeg
        .input('pipe:',format='rawvideo',pix_fmt='bgr24',s='{}x{}'.format(width,height))
        .output(
            vcodec='libx264', # [libx264,rawvideo,h264_nvenc]需要进一步测试，好像只有rawvideo才能随便设置ts长度，其他压缩格式各自有自己的最小长度，比如h264_nvenc最小10秒
            format='segment', 
            pix_fmt='rgb24', 
            segment_list=streaming_server_url+"/Playlist.m3u8", # 创建streaming server播放列表
            segment_time=1, # 每秒创建一个ts片段
            r=fps, # frame_rate fps
            start_number=0, # 需要在实际项目中改为你插入的点
            force_key_frames='expr:gte(t,n_forced*1)', # 强制每秒插入1个i帧，这句不知道对不对
            filename=streaming_server_url+"/stream_%03d.ts" # 创建ts片段，发送到streaming server
            )
        .overwrite_output() 
        .run_async(pipe_stdin=True) 
        )
    # 将25帧视频numpy数据顺序写入ffmpeg pipe
    for index in range(len(images_batch)): # len(images_batch)=25
        img=images_batch[index] # [256,256,3]
        process.stdin.write(
            img # bgr24
            .astype(np.uint8)
            .tobytes()
        )
    process.stdin.close() 
    process.wait() 
    return 

################################################################################################
# 以下为Triton模板代码，只保留初始化必须的参数和execute方法中最基本的pb_tensor转换代码，不要写太多的业务逻辑 #
################################################################################################
import triton_python_backend_utils as pb_utils # package come from inside docker
import json

class TritonPythonModel:  
    def initialize(self, args):
        self.streaming_server_url="rtmp://127.0.0.1:8080/character_ID" # 如果多character，可以放在execute的input中获得推流地址
        pass

    def execute(self, requests):
        responses = []
        for request in requests: 
            # 假设传入audio为时长1秒/16k采样数据，传入25fps下1秒图像数据images_batch [25,256,256,3]
            audio = pb_utils.get_input_tensor_by_name(request, 'audio').as_numpy() # [16000]
            images_batch = pb_utils.get_input_tensor_by_name(request, 'images_batch').as_numpy() # [25,256,256,3]
            # get torch result
            streaming(images_batch,audio,self.streaming_server_url)
        # 这里是空返回值，如果需要告诉主线程已经处理结束的话，可以返回1
        return responses

    def finalize(self):
        pass

