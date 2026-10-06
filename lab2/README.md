# Lab 2 — final PNG submission

## 提交哪几个文件

`submission/` 中的 **4 张 PNG** 就是最终提交文件，每张都以对应编号开头：

| 文件 | 对应作业要求 |
| --- | --- |
| `1_depth_edges.png` | 原场景 + 改善后的代码 depth edges |
| `2_ai_depth_edges.png` | 原场景 + 从 RGB 直接生成的 AI depth edges |
| `3_reconstruction_depth_edges.png` | 代码 depth edges 输入 + AI 重建结果 |
| `4_reconstruction_all_edges.png` | ALL edges 输入 + AI 重建结果 |

四张图均为 3320 × 1520 PNG，包含简短英文方法说明或比较结论。直接上传四张 PNG；`lab2_submission.zip` 是方便分享和保存的同一组文件，ZIP 内只有这四张图。不要用旧 Claude 结果或调试图替代最终提交图。

快速比较两种重建：`output/reconstruction_comparison.png`。查看 Claude 原结果和改善代码结果：`output/comparison.png`。

## 本次实际比较结果

两张重建图都保留了木块整体的弯折布局和右侧向上弯曲的部分。Depth edges 的重建呈现较平滑的木纹和桌面；ALL edges 的重建呈现更明显的木纹条带和桌面颗粒。两者都改变了部分木块形状、姿态和背景，尤其是屏幕位置与教室家具，不能视为精确恢复原照片。

可直接使用的英文比较：

> Both reconstructions preserved the overall bent arrangement of the wooden blocks. In this pair, the reconstruction from depth edges had smoother wood surfaces and a smoother tabletop, while the reconstruction from ALL edges showed stronger wood-grain patterns and tabletop speckles. ALL edges supplied more appearance-related detail, but some texture was exaggerated. Both reconstructions changed individual block details and the classroom background, so neither exactly recovered the original photograph. This is a qualitative comparison of one generated pair, not a general accuracy result.

## 代码与 AI 的对应关系

- Part 1：四方向照片通过 Python/OpenCV 计算，未使用生成式 AI 补画或手工描线。
- Part 2：内置 `image_gen` 工具只以原 RGB 图为图像参考，直接推断 depth edges；这是本次真正新增的 AI 图，不是旧 Claude BMP 的格式转换。
- Parts 3–4：使用内置 `image_gen` 重建。边缘由 Python 计算；重建由图像生成模型完成。每次调用的 `referenced_image_paths` 仅包含对应的单张边缘图；没有提供 RGB 照片或另一张重建图作为参考。
- 两次重建的 prompt 和颜色/材质提示完全相同；Part 2 的 AI 边缘图没有用于这两次重建。
- 精确 prompts、输入与输出路径记录在 `output/ai/generation.json`。使用的是内置图像生成工具，不是 CLI/API fallback；未假定或声称未公开的具体底层模型版本。
- AI 边缘和 AI 重建都是推断结果，不是实测深度或 ground truth。工具调用位于同一会话，本记录不声称已独立审计模型内部上下文隔离。

## 改善了哪些代码

输入方向按用户重命名后的文件确认：

| 光源方向 | 文件 |
| --- | --- |
| left | `images/IMG_2082_left.jpg` |
| right | `images/IMG_2084_right.jpg` |
| top | `images/IMG_2083_top.jpg` |
| bottom | `images/IMG_2086_bottom.jpg` |

`depth_edges_confidence.py` 默认流程：

1. 等比例缩小到 1600 × 1200，以 left 照片为参考。
2. SIFT 匹配 + RANSAC homography 配准其余三张照片。特征选择矩形覆盖主体和桌面，只用于找匹配；没有把主体外区域从结果中裁掉。
3. Gaussian sigma = 3.0 降噪；每张灰度图除以四图最大值，分母下限为 0.02。
4. 课程方向 Sobel：left +x、right -x、top +y、bottom -y。
5. 方向局部极大值细化，hysteresis 阈值 0.05 / 0.2，删除少于 35 像素的连通分量；去掉无效配准边界。

这是在课程比值/Sobel 方法上的工程改进；不是未经修改的课程默认参数。特征内点的中位配准误差约 0.16–0.28 px（1600 × 1200 工作分辨率），不等于所有像素或所有深度层都已精确对齐。单一 homography 无法完整修复视差。

`all_edges.py` 将同一张 left 照片缩小到 1600 × 1200，再进行灰度、3×3 Gaussian 和 Canny 50/150。由于只有带方向光照的照片，这个输入不是独立拍摄的 ambient-only 图。

默认代码结果保存在 `output/code/`；新 confidence PNG 将理论正 Sobel 范围 0–4 映射为 0–255。`processing.json` 记录实际参数、变换矩阵和特征匹配信息。

白色边缘像素占比：重新筛选后的 depth edges 约 0.97%，ALL edges 约 6.69%。这是边缘稀疏程度，不是准确率。降噪也会删除弱小真实边缘，改善图仍有缺失和少量伪边缘。

## Part 1 的重新筛选

之前版本偏重噪声抑制，弱轮廓保留不足，因此本次重新选优。比较了 24 组组合：Gaussian sigma 为 1.2、2、3、4；low/high 阈值对为 0.03/0.12、0.05/0.2、0.08/0.25、0.12/0.3、0.15/0.4、0.2/0.5，连通分量阈值固定为 35。另检查 6 组基于最大合成图 Canny 的位置支持过滤结果，因造成额外轮廓断裂而放弃。

最终选择 sigma=3、low=0.05、high=0.2、min_component=35。选择依据是左端上沿与中间连接处的连续性改善，同时右上木块面内的木纹线减少；并不是边缘越少越好。原图、旧版及两组入围候选的左右局部均已放大检查。仍有阴影边界偏移和缺失，没有 ground truth，不能声称全局最优或准确率提高。

前后图：`output/part1_selection.png`；参数与筛选理由：`output/part1_selection.json`。最终提交仍只有 `submission/1_depth_edges.png` 这一张 Part 1 图，没有把候选混入 submission/。

本次只重新筛选 Part 1。Part 3 保留原先实际用于重建的边缘输入（`output/ai/reconstruction_depth_input.png`）和对应重建，避免把新边缘图误标为旧重建的输入。因此 Part 1 的最佳边缘与 Part 3 所用的早期候选不同；Part 2–4 的提交 PNG 内容未改变。完整 ZIP 已更新。

## 运行与复现

在本目录执行：

```bash
python -m pip install -r requirements.txt
python depth_edges_confidence.py images/IMG_2082_left.jpg images/IMG_2084_right.jpg images/IMG_2083_top.jpg images/IMG_2086_bottom.jpg
python all_edges.py images/IMG_2082_left.jpg
python make_comparison.py
```

`make_comparison.py` 使用已保存的 AI 输出生成四张最终 PNG、两张查看用对比图及 ZIP。它不会重新调用 AI；若要重做生成步骤，应使用 generation.json 中的提示词与指定参考图，生成结果不会保证逐像素一致。

原始课程计算仍可单独运行，不覆盖最终结果：

```bash
python depth_edges_confidence.py images/IMG_2082_left.jpg images/IMG_2084_right.jpg images/IMG_2083_top.jpg images/IMG_2086_bottom.jpg --raw --threshold 0.8 --output-dir /tmp/lab2_raw
```

课程依据位于 `../../course_files_export/TH Lab 2/depthEdgesKey.ipynb`。当前 `make_comparison.py` 已替代旧的查看图排版逻辑，不再使用旧分辨率和阈值说明。

## 文件保留与验证

- `images/*.jpg` 与 `images/originals/*.HEIC`：计算输入和相机原件。
- `reference/assignment.png`：作业要求截图。
- `output/claude/`：用户确认由 Claude 提供的旧结果，保留作为前后比较；未冒充新 AI 结果。
- `output/code/`：代码边缘、confidence 与实际处理参数。
- `output/ai/`：AI 边缘、两张重建及生成记录。
- `output/submission_manifest.json`：四张最终提交图的尺寸、文件大小和 SHA-256。

已完成的检查：课程样例与独立 NumPy Sobel 参考的二值结果一致；已知平移的配准恢复误差小于 0.5 px；两张代码边缘图均为 1600 × 1200 的 0/255 二值 PNG；重新筛选的 depth edges 的非背景连通分量均不少于 35 像素。最后检查四张提交图的排版、PNG 解码完整性及 ZIP 条目与原文件逐字节一致性。

之前已删除两张与保留 PNG 逐像素相同的 BMP。本次未删除原始照片或 Claude 对比证据。
