
- English
- [中文](README_zh.MD)

# Tp Manager

*If it's useful, please give a star :)*

## Feature

- Teleport between players

## TODO

- Check if target player exists
- Manage in game way points
- Linking with login_proxy?

## Dependencies

| ID | Release Link |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## Commands

> [!TIP]
> Some other plugins also registered `!!tp` as root command. To avoid conflict, you also can use `!!tpm` to replace `!!tp`

|         Command format | Introduction |
|------------------------|-----|
| `!!tp help`            | Show help message, aka `!!tp` |
| `!!tp pos <x> <y> <z>` | Teleport to `<x>`, `<y>`, `<z>` |
| `!!tp ask <name>`      | Send an teleport request, aka `!!tpa` |
| `!!tp askhere <name>`  | Send an teleport request to here, aka `!!tph` |
| `!!tp accept`          | Accept the teleport request |
| `!!tp reject`          | Reject the teleport request |
| `!!tp cancel`          | Cancel your teleport request |

## Config files

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // Command permissions
        "pos": 2,
        "ask": 1,
        "askhere": 1,
        "accept": 1,
        "reject": 0,
        "cancel": 0
    },
    "teleport_cooldown": 60, // in sec, the minimum teleport operation interval
    "teleport_expiration": 10, // in sec, the teleport request expiration
    "teleport_commands": [ // Command list for teleport players
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // Command for teleport position
}
```
