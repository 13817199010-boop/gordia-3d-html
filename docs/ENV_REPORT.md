# P0 云端检测
工作目录 /workspace/gordia-3d-html。同步前工作树干净，main 初始同步至 77d9294。所有指定文档、立绘、海报、PV、七张 PNG 均已到位。Pillow 实际打开并校验了图像，FFprobe 读取到 H.264 1440×2038 / AAC，时长 13.405922 秒；FFmpeg 解码了 8.65 秒画面。
 
|组件|实测|
|---|---|
|Blender / 内置 bpy|后台进程 4.3.2|
|Python / Pillow|3.12.14 / 12.3.0|
|FFmpeg / FFprobe|7.1.5|
|Node / npm|24.19.0 / 11.9.0|
|浏览器工具|Playwright 1.65.1、系统 Chromium 154|
|Web 与 glTF 工具|Three 0.187.0、Vite 8.3.8、@gltf-transform/cli 4.5.1、gltf-validator 2.0.0-dev.3.10；安装于同机 /workspace/scratch/gordia-tools|
|Git / GitHub|Git 2.52.0，已认证并从 origin 拉取|
|Context7|查询 /mrdoob/three.js 的 GLTFLoader 加载及异常回调|
|计算设备|无 nvidia-smi、/dev/nvidia* 或 /dev/dri。未发现可运行 Hunyuan3D / TRELLIS.2 的本机免费 GPU。采用 bpy + CPU，无生成 API 调用。|

仓库中另已固定上述 Node 工具的版本，使用 npm ci 可从 package-lock.json 还原。单文件 HTML 的离线验收通过向浏览器载入文件内容完成；本机受管 Chromium 禁止直接导航至 file:// URL。
