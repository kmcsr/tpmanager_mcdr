
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
- 与login_proxy联动?

## 依赖

| ID | 下载链接 |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## 指令

|                指令格式 | 介绍 |
|------------------------|-----|
| `!!tp help`            | 显示帮助信息, `!!tp`同 |
| `!!tp pos <x> <y> <z>` | 传送到`<x>`, `<y>`, `<z>` |
| `!!lp ask <name>`      | 请求传送到玩家 |
| `!!lp askhere <name>`  | 请求玩家传送到你 |
| `!!lp accept`          | 同意传送请求 |
| `!!lp reject`          | 拒绝传送请求 |
| `!!lp cancel`          | 取消传送请求 |

## 配置文件

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // 指令权限
        "pos": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
        "reject": 0,
        "cancel": 0
    },
    "teleport_expiration": 10, // 秒, 传送请求过期时间
    "teleport_commands": [ // 用于传送到玩家的指令集
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // 用于传送到坐标的指令
}
```
