# Risky Streak Enhancement

## 💀 **Risky Streak System Added**

### **New Risky Streak Configuration:**

```json
{
  "risky_streak": {
    "name": "Risky Streak",
    "type": "risky",
    "entry_amount": 10,
    "target_amount": 50000,
    "max_legs": 15,
    "base_multiplier": 1.8,
    "risk_level": "risky"
  }
}
```

### **Key Features:**

#### 1. **High-Risk, High-Reward**
- **Entry Amount:** $10 (vs $1 for safe streaks)
- **Target Amount:** $50,000 (vs $500-$2000 for safe streaks)
- **Max Legs:** 15 legs (vs 8-13 for safe streaks)
- **Base Multiplier:** 1.8x (vs 1.35x-1.6x for safe streaks)

#### 2. **Enhanced Risk Management**
- **Progressive Risk:** 8% increase per leg (vs 5% for safe streaks)
- **Multiplier Cap:** Capped at 3.0x to prevent unrealistic values
- **Higher Confidence Requirements:** 90%+ confidence target
- **Separate Tracking:** Completely separate from safe streaks

#### 3. **Visual Distinction**
- **Risk Emoji:** 💀 for risky streaks (vs 🔥 for safe streaks)
- **Separate Sections:** Safe and risky streaks displayed separately
- **Risk Level Display:** "RISKY" prominently shown in messages

### **Risky Streak Message Format:**

```
💀 **Risky Streak** 💀

**Entry:** $10 | **Target:** $50,000 | **Multiplier:** 1.8x
**Risk Level:** RISKY

**Game:** Team A vs Team B
**Player:** Player Name
**Prop:** Prop Type
**Line:** X.X
**Pick:** Over/Under
**Confidence:** 95%
**Odds:** X.XX

**Progress:** 3/15 legs
**Status:** ✅✅🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒
**Total Multiplier:** 5.83x
**Potential Payout:** $58.30

**Reasoning:** Detailed explanation

---
```

### **System Architecture:**

```
Enhanced Streak System
├── Safe Streaks (6 types)
│   ├── 3 Streak Starters ($1 entry, $500-$2000 target)
│   └── 3 One Legs ($1 entry, $500-$1000 target)
└── Risky Streaks (1 type)
    └── 1 Risky Streak ($10 entry, $50,000 target)
```

### **Key Benefits:**

1. **High-Risk Option:** Provides a high-risk, high-reward streak option
2. **Separate Management:** Risky streaks managed independently from safe streaks
3. **Enhanced Multipliers:** Higher base multipliers and progression
4. **Visual Distinction:** Clear visual separation with emojis and formatting
5. **Confidence Requirements:** Higher confidence targets for risky picks
6. **Realistic Caps:** Multiplier caps prevent unrealistic values

### **Multiplier Progression Example:**

```
Leg 1: 1.8x → Win ✅
Leg 2: 1.94x → Win ✅
Leg 3: 2.10x → Win ✅
Leg 4: 2.27x → Pending 🔒
Total Multiplier: 7.33x
Potential Payout: $73.30
```

### **Discord Integration:**

- **Separate Sections:** Safe and risky streaks shown separately in summaries
- **Risk Emojis:** 💀 for risky, 🔥 for safe
- **Enhanced Formatting:** Clear risk level display
- **Immediate Posting:** Same immediate posting system for both types

The risky streak system provides a high-risk, high-reward option while keeping it completely separate from the safe streaks, using the same multiplier calculations as our confidence system! 💀 