# Linux 服务器迁移评估

## 当前状态
- 运行环境：MacBook Pro (Apple Silicon, macOS Sequoia)
- 全栈服务：OpenClaw + Paperclip + OpenFang + Symphony + PostgreSQL + SearXNG
- 依赖：colima (Docker), LaunchAgents, Homebrew

## 迁移动机
1. MacBook 不适合 7×24 运行（电池、散热、合盖休眠）
2. Docker 性能在 macOS 上有 overhead（colima/VM）
3. 无法远程访问（除非开 Tailscale）
4. 开发和生产环境混用

## 方案对比

### A. VPS (推荐起步)
- **提供商**: Hetzner / Vultr / DigitalOcean
- **配置**: 4C8G 足够当前负载
- **成本**: ~$20-40/月
- **优点**: 24/7 在线、公网 IP、Docker 原生
- **缺点**: 网络延迟、需要部署自动化

### B. Homelab (长期推荐)
- **硬件**: Intel NUC / Raspberry Pi 5 / 旧笔记本
- **成本**: 一次性 $100-500 + 电费
- **优点**: 零月费、完全控制、内网低延迟
- **缺点**: 需要 UPS、公网需 DDNS/Tailscale

### C. 混合方案 (推荐)
- VPS 跑核心服务（OpenClaw Gateway、Paperclip UI）
- MacBook 跑 Codex（需要本地 GPU/大内存）
- Tailscale 打通网络
- 渐进迁移，不一步到位

## 迁移步骤（渐进式）
1. **Phase 1**: 在 VPS 上部署 Paperclip + PostgreSQL（最独立的服务）
2. **Phase 2**: 迁移 OpenFang + SearXNG（纯 Docker 服务）
3. **Phase 3**: 配置 OpenClaw Gateway 远程模式
4. **Phase 4**: Symphony 迁移（需要 Codex 通信）
5. **Phase 5**: 完全远程化，MacBook 只做开发

## 依赖项
- [ ] 选择 VPS 提供商并开通
- [ ] Docker Compose 编排文件
- [ ] Tailscale 网络配置
- [ ] 数据备份/恢复流程
- [ ] CI/CD 部署自动化

## 建议时间线
- 本周：选定 VPS，Phase 1
- 下周：Phase 2-3
- 月底：评估是否继续 Phase 4-5

## 预算估算
| 项目 | 月费 |
|------|------|
| VPS (4C8G) | $30 |
| Tailscale | $0 (免费 tier) |
| 域名 | $1 |
| **合计** | **~$31/月** |
