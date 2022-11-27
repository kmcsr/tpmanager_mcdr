
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

## Dependencies

| ID | Release Link |
|----|----|
| [kpi](https://github.com/kmcsr/kpi_mcdr) | <https://github.com/kmcsr/kpi_mcdr/releases> |

## Config files

#### tpm/config.json

```javascript
{
    "minimum_permission_level": { // Command permissions
        "help": 0,
        "ask": 1,
        "accept": 1,
        "reject": 0
    },
    "teleport_command": "tp {src} {dst}" // Teleport command
}
```
