# 像素贪吃蛇（PWA）

经典像素风贪吃蛇，纯前端单页，可「安装」到 Android 桌面像原生 App 一样全屏启动，装过之后断网也能玩。

- 操作：环形四分 D-pad（上下键按视觉平衡向中心收拢，环形整体纵向压扁 15%；也支持键盘方向键 / WASD / 在棋盘上滑动）；点一下棋盘即暂停
- 规则：撞墙即死；吃到红果变长并按得分档位提速；每吃到 3 个红果，棋盘上会出现一个**限时黄块**，吃到 +5 分但只长 1 节、不改变速度等级
- 纪录：最高分按难度分别记录（普通榜 / 困难榜互不影响）
- 难度：普通 / 困难（困难起步更长更快，且每得 6 分在棋盘上长出一个障碍）
- 视觉：深色背景，蛇为霓虹绿，食物为霓虹红，障碍为红框叉块

## 三步先跑起来

1. 双击 `start-server.cmd`（本机需要 Python；等价命令：`python -m http.server 8123 --bind 127.0.0.1`）
2. 浏览器打开 <http://127.0.0.1:8123/index.html>
3. 点「开始游戏」

> 直接双击 `index.html` 也能玩，但 `file://` 下 Service Worker 不生效，装桌面/离线这两项用不了。

## 装到 Android 桌面（关键一步）

浏览器只在**安全上下文**（https，或 localhost）里允许把网页装成独立 App。所以「手机上能装」需要一个 https 地址，把整个 `snake/` 目录原样传上去即可，不需要任何构建：

| 方式 | 做法 | 适合 |
| --- | --- | --- |
| GitHub Pages | 建仓库 → 上传这些文件 → Settings → Pages → 选分支根目录 → 拿到 `https://用户名.github.io/仓库名/` | 免费、长期在线 |
| Vercel / Netlify / Cloudflare Pages | 拖文件夹进网页后台，得到 https 域名 | 两分钟搞定 |
| 静态服务器 / 对象存储 | 任意能开 https 的静态托管，保持目录层级不变 | 已有服务器 |

拿到 https 地址后，在 Android Chrome 里：

1. 打开该地址，先玩一局（触发缓存）
2. 右上角菜单 →「安装应用」（部分机型显示为「添加到主屏幕」）
3. 桌面上出现图标，点开是全屏无地址栏的独立窗口

排查：菜单里没有「安装应用」时，通常是 https 未生效、`manifest.webmanifest` 返回 404、或图标路径不通；在 Chrome 里开 `chrome://inspect` 或看 DevTools → Application → Manifest 会直接报原因。

> 同一 Wi-Fi 下用手机访问电脑的 `http://192.168.x.x:8123` 只能玩，**不能安装**（局域网 http 不是安全上下文）。想用手机当场安装，得走上面的 https 方案。

## 目录结构

```
snake/
├── index.html              # 全部游戏代码（结构 + 样式 + 逻辑，单文件）
├── manifest.webmanifest    # PWA 清单：名称、图标、standalone 全屏、竖屏
├── sw.js                   # Service Worker：首次访问后离线可玩
├── icons/                  # 图标（192/512/180，含 maskable）
├── tools/make_icons.py     # 重新生成图标的脚本
└── start-server.cmd        # Windows 下一键本地起服务
```

## 想改点什么

游戏参数都在 `index.html` 脚本开头的几行常量里：

```js
var COLS = 22, ROWS = 22, CELL = 16;      // 棋盘 22×22 格，每格 16px
var TIER_GAPS = [8, 6, 4, 3, 2, 2, 1];    // 升第 2/3/4…级各需再吃几分，用尽后每 1 分一级
var RING_SQUASH = 0.85;                   // 环形方向键纵向压扁系数（1 = 正圆，越小上下键越靠中心）
var BONUS_EVERY = 3;                      // 每吃几个红果刷一个限时黄块
var BONUS_TTL_BASE = 10, BONUS_TTL_MIN = 4; // 黄块存在 10 秒，每 2 个速度等级 -1 秒，最低 4 秒
var STORE_KEY = 'snake.best.v1';          // 旧版单值最高分（自动迁移到普通榜）
var BONUS_KEY = 'snake.best.v2';          // 分难度最高分 {normal, hard}
var DIFF_KEY = 'snake.diff.v1';           // 上次选择的难度
```

速度公式：`tick = max(min, base - 等级 × step)`，单位毫秒/格，数值越小蛇越快；等级由累计得分按 `TIER_GAPS` 推出。

| 难度 | 起步 tick | 每级减速 | 最快 tick | 初始身长 | 障碍 |
| --- | --- | --- | --- | --- | --- |
| 普通 | 150 | 7 | 66 | 3 节 | 无 |
| 困难 | 118 | 9 | 50 | 5 节 | 最多 8 个，每 6 分生成一个 |

配色在 `<style>` 开头的 `:root` 里（`--neon` 蛇/强调色、`--food` 食物色、`--bg` 背景）。

**改完记得改 `sw.js` 里的 `const CACHE`**（例如 `snake-v1` → `snake-v2`）。Service Worker 会优先用缓存，不改版本号的话，已经装过的设备会一直跑旧代码。

## 版本历史

```
v0-core        核心玩法：移动、撞墙/撞身判定、计分、最高分持久化
v1-playable    屏幕方向键、滑动转向、暂停、像素风视觉
v2-pwa         manifest、离线缓存、图标，可安装到桌面
v3-final       开始页/结束页信息修正、README、一键本地启动
v4-difficulty  环形四分 D-pad、点棋盘暂停、棋盘 22×22、得分档位提速、普通/困难难度
v5-bonus       分难度最高分、限时奖励黄块（+5 分/不加速）、HUD 重排
v6-dpad        方向键纵向压扁 15%，上下键向中心收拢（方案 A）
```

回退到任意版本：

```bash
git reset --hard v1-playable
```

## 开发辅助

带 `?dev=1` 打开时，页面会暴露一个调试对象，方便自动化测试（正常游玩不受影响）：

```js
window.__dev.state()            // { snake, food, score, best, alive, running, tick, dir, obstacles, diff }
window.__dev.placeFoodAt(x, y)  // 把食物挪到指定格
window.__dev.placeObstacleAt(x, y) // 放一个障碍（困难模式调试用）
window.__dev.placeBonusAt(x, y) // 放一个奖励黄块
window.__dev.bonusTtlMs()       // 当前等级/难度下黄块的存活毫秒数
window.__dev.levelForScore(s)   // 第 s 分对应的等级（0 起）
window.__dev.tickFor(s)         // 第 s 分对应的 tick
window.__dev.step()             // 手动走一步
window.__dev.start()            // 立即开局
```

重新生成图标（需要 Pillow）：

```bash
python tools/make_icons.py
```
