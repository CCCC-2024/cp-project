# Lab 4 报告参考素材（给写文档的组员）

> ⚠️ 模板要求 **"2 Features" 由组员自己写，不能用 AI**。下面第 1 部分只是**观察要点和数据**（看哪里、看到什么、为什么），请用自己的话写成段落，不要直接复制。
> 第 2 部分"局限性"不受这个限制，可以参考或直接使用。
> 数值都在线性亮度下测量，用的是 `output/separation_linear.npy`；"占比"指 Global / Floodlit。

---

## 第 1 部分：Features 观察要点

### 1.1 Specularities（高光）→ 出现在 Direct 里

**看哪里**（对照 `output/direct.png` 和 `output/global.png`）：
- 苹果左前方的小亮点
- 马克杯**内沿的弧形亮线**，以及杯子内部一道竖直的反光
- 香薰罐**金属盖的边缘**
- 画面左下、右下的**银色金属踢脚线边缘**
- 白纸上手电筒的**圆形光斑**：直射光本身的照明图案

**看到了什么**：这些是 Direct 图里最亮的像素；在 Global 图里对应位置没有高光。

**为什么**：高光是镜面反射，光从光源出发，在表面反射一次就进入相机，属于单次反射，所以是 Direct。笔影扫过时，直射光被挡住，高光随之消失，所以它会出现在 `max − min` 里。

### 1.2 Shadows（阴影）→ Direct 里是暗的

**看哪里**：
- **公仔投在红纸上的影子**：公仔头部和身体左侧的红纸区域
- 苹果和桌面接触处的影子
- 苹果背光的一侧（自身阴影）

**数据**（公仔投影 vs 旁边被照亮的红纸）：

| | Floodlit | Direct | Global |
|---|---|---|---|
| 公仔投影内 | 0.023 | 0.019 | 0.004 |
| 旁边被照亮的红纸 | 0.102 | 0.084 | 0.018 |

投影区域的 Direct 大约暗了 **4.4 倍**。

**为什么**：投影里的点"看不到"光源，收不到单次反射的光，只剩别处反弹过来的光。

**写的时候可以诚实补一句**：理论上，Global 在投影内外应该差不多。但我们的 Global 在投影里也偏暗（0.004 vs 0.018），原因见第 2 部分第 1、2 条。

### 1.3 Interreflections（互反射）→ 出现在 Global 里

**看哪里**（`output/global.png`）：
- **马克杯被映成黄色**：杯身在 Global 里明显泛黄，在 Direct 里是中性的白色。
  - 数据：杯身的蓝/红比，Floodlit 里是 0.42，Global 里是 **0.05**，数值越低越黄。
  - 原因：马克杯正前方就是黄色信封，信封被照亮后把黄光反射到杯子上。
- **白纸和红纸的墙角发红**：Global 里靠近红纸的白纸和墙角带着红色，这是颜色渗透。
- **马克杯内部发亮**：杯子内壁是凹面，光在里面来回反射多次。

**为什么**：Global 是先照到别的表面、再反弹过来的光。反弹一次，光就带上了第一次照到的那个表面的颜色，所以白色的表面会被"染"成黄色或红色。

---

## 第 2 部分：Limitations（可直接使用的英文草稿）

**1. Hand-held light source.** The phone flashlight was held by hand. Its brightness varied by about ±10% during each sweep. We divided out this global flicker frame by frame, using pixels that were not in the occluder's shadow. Changes in the light's *direction* cannot be corrected this way, however: they slightly move highlights and shadow edges between frames, which can leave some spurious direct light near cast-shadow boundaries.

**2. Occluder width trade-off.** In a first capture with a thin pen, the shadow never became fully dark inside the flashlight's hot spot. Seen from there, the whole lens of the flashlight is lit and looks wider than the pen, so the pen formed only a penumbra, and part of the direct light leaked into the global image as a visible bright disk. We switched to a wider (about 1.5–2 cm) occluder, which produces a true umbra everywhere (the shadow now removes about 96% of the light even in the hot spot). The cost is a wider shadow: up to about 12% (horizontal sweep) and 25% (vertical sweep) of the frame was shadowed at the same time. This also blocks part of the indirect light, so our global image is probably an underestimate (it is about 6% of the floodlit image overall), and cast shadows stay darker in the global image than theory predicts. The clearest evidence is a pixel inside the doll's cast shadow on the red paper. It is never lit directly, yet its brightness falls slowly, over about 200 frames, to 30–40% as the wide shadow covers the surrounding surfaces that bounce light onto it. A directly lit pixel instead drops sharply to its floor in a few frames. That slow loss of indirect light is wrongly counted as "direct" inside cast shadows.

**3. Exposure and bit depth.** The final capture was about 1.5 stops underexposed. To keep precision in the dim global image, we decoded the 10-bit video at 16 bits per channel instead of 8.

**4. Linearization.** Separation has to be done in linear light. We assumed a gamma of 2.2 for the camera's "Normal" colour profile. However, the tone setting was "Vivid", which adds extra contrast and saturation, and DJI does not publish the exact curve. So the absolute direct/global ratios carry some uncertainty; which regions are direct and which are global is not affected.

**5. Shadow camera (extra credit).**
- The occluder was swept by hand. We assumed constant speed and mapped one video frame to one light-view pixel on both axes, so non-uniform speed shows up as mild stretching.
- Both sweeps were tilted by about 12.7°. We rolled the virtual camera about its optical axis to level the image.
- The black regions in the light view are of two kinds. Some are surfaces the light sees but the camera does not. The others are pixels whose shadow timing is unreliable: specular surfaces (the metal lid), the mug interior, and depth edges. We left them black instead of hallucinating content.

---

## 第 3 部分：Extra credit 可以写的观察（参考 `output/shadow_camera/comparison.png`）

1. **视角变了**：光源在左上方，结果像从左上方往下看。墙角、桌面的透视都变了，马克杯看起来更"高"。
2. **投影消失了**：光源看不到它照不到的地方，所以相机视角里公仔、苹果的投影，在光源视角里都不存在。论文图 3 指出的就是这个现象。
3. **实现步骤**（写 "How you implemented" 时用）：
   - 每个像素找出笔影经过的亚帧时刻 `t_h`、`t_v`：在 5 帧平滑后的亮度曲线上，取最暗点所在的连续阴影段，计算加权中心；
   - 把 `(t_h, t_v)` 当作光源视角的像素坐标；
   - 在这个坐标系里对相机像素做 Delaunay 三角剖分，每个光源视角像素反查对应的相机位置，再从 Floodlit 取色（Helmholtz 互易性：`I_light(t_h, t_v) = I_camera(x, y)`）；
   - 在相机图像里被拉得很长的三角形跨越了深度边界，这些位置留黑。
