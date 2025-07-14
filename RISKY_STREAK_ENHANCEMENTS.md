# Risky Streak Enhancements

## 💀 **Risky Streak System Complete!**

### **New Risky Streak Features:**

#### 1. **Risky Streak Configuration**
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

#### 2. **Key Features**
- **$10 Entry Amount:** Higher stakes for bigger rewards
- **$50,000 Target:** Massive payout potential
- **15 Max Legs:** Longer streak for bigger multipliers
- **1.8x Base Multiplier:** Higher starting multiplier
- **8% Risk Progression:** More aggressive multiplier increases per leg
- **Separate from Safe Streaks:** Completely isolated system

#### 3. **Risk Level Separation**
- **Safe Streaks:** $1 entry, conservative picks, reliable props
- **Risky Streaks:** $10 entry, aggressive picks, high-upside props
- **Different AI Prompts:** Separate logic for each risk level
- **Visual Distinction:** 💀 emoji for risky, 🔥 for safe

#### 4. **Enhanced Multiplier System**
```python
# Safe streaks: 5% increase per leg
risk_factor = 1.0 + (current_leg * 0.05)

# Risky streaks: 8% increase per leg  
risk_factor = 1.0 + (current_leg * 0.08)
```

#### 5. **Discord Integration**
- **Separate Posting:** Safe streaks posted first, then risky with warning
- **Risk Warning:** "💀 **RISKY STREAKS** 💀" header
- **Visual Indicators:** 💀 emoji and ⚠️ warnings
- **Separate Summaries:** Safe and risky streaks shown separately

### **Risky Streak Message Format:**

```
💀 **Risky Streak** 💀

**⚠️ HIGH RISK - $10 ENTRY ⚠️**

**Entry:** $10 | **Target:** $50,000 | **Multiplier:** 1.8x

**Game:** Team A vs Team B
**Player:** Player Name
**Prop:** Prop Type
**Line:** X.X
**Pick:** Over/Under
**Confidence:** 85%
**Odds:** X.XX

**Progress:** 3/15 legs
**Status:** ✅✅🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒
**Total Multiplier:** 2.25x
**Potential Payout:** $22.50

**Reasoning:** Detailed explanation

---
```

### **System Architecture:**

```
Enhanced Streak System
├── Safe Streaks (6 total)
│   ├── 3 Streak Starters ($1 entry, $500-$2000 targets)
│   └── 3 One Legs ($1 entry, $500-$1000 targets)
├── Risky Streaks (1 total)
│   └── 1 Risky Streak ($10 entry, $50,000 target)
└── Multiplier System
    ├── Safe: 5% increase per leg
    ├── Risky: 8% increase per leg
    └── Same confidence calculations
```

### **Key Benefits:**

1. **Risk Separation:** Safe and risky streaks completely isolated
2. **Higher Stakes:** $10 entry for bigger rewards
3. **Massive Payout:** $50,000 target potential
4. **Aggressive Multipliers:** 8% increase per leg for risky
5. **Visual Distinction:** Clear indicators for risk levels
6. **Separate AI Logic:** Different prompts for safe vs risky

### **Example Risky Streak Progression:**

```
Leg 1: 1.8x multiplier → Win ✅
Leg 2: 1.94x multiplier → Win ✅  
Leg 3: 2.10x multiplier → Win ✅
Leg 4: 2.27x multiplier → Pending 🔒
Total Multiplier: 7.35x
Potential Payout: $73.50
Status: ✅✅✅🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒🔒
```

### **Risk Management:**

- **Safe Streaks:** Conservative picks, reliable props, lower multipliers
- **Risky Streaks:** Aggressive picks, high-upside props, higher multipliers
- **Separate Tracking:** No mixing between safe and risky
- **Different AI Prompts:** Tailored logic for each risk level
- **Visual Warnings:** Clear indicators for risky streaks

The system now has complete separation between safe and risky streaks, with the risky streak offering $10 entry targeting $50,000 payout using the same confidence-based multiplier calculations! 💀🚀 