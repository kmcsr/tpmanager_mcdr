
- [English](README.MD)
- 中文

# Tp Manager

*如果本插件有用, 请给个star吧 :)*

## 特性

- 玩家之间的传送

## TODO

- 检查目标玩家是否存在
- 传送冷却
- 管理游戏内路径点功能

## 依赖

| ID | 下载链接 |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## 配置文件

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // 指令权限
        "help": 0,
        "ask": 1,
        "accept": 1,
        "reject": 0
    },
    "teleport_command": "tp {src} {dst}" // 用于传送的指令
}
```
