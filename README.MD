
- English
- [中文](README_zh.MD)

# Tp Manager

*If it's useful, please give a star :)*

## Feature

- Teleport between players

## TODO

- Check if target player exists
- Teleport cooldown
- Manage in game way points
- Linking with login_proxy?

## Dependencies

| ID | Release Link |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## Commands

|         Command format | Introduction |
|------------------------|-----|
| `!!tp help`            | Show help message, aka `!!tp` |
| `!!tp pos <x> <y> <z>` | Teleport to `<x>`, `<y>`, `<z>` |
| `!!lp ask <name>`      | Send an teleport request |
| `!!lp askhere <name>`  | Send an teleport request to here |
| `!!lp accept`          | Accept the teleport request |
| `!!lp reject`          | Reject the teleport request |
| `!!lp cancel`          | Cancel your teleport request |

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
    "teleport_expiration": 10, // in sec, the teleport request expiration
    "teleport_commands": [ // Command list for teleport players
        "say Teleporting {src} to {dst} ...",
        "tp {src} {dst}",
    ],
    "teleport_xyz_command": "tp {name} {x} {y} {z}" // Command for teleport position
}
```
