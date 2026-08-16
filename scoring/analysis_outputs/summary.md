# AdverseMed-500 analysis summary — inference_outputs/adversemed_500

**Runs:** 20 across 5 models × 4 methods

## Per-run headline metrics

| Model | Method | n_use | Acc | Abst | ECE | Brier | AURC | Risk@90 | Cost |
|---|---|---|---|---|---|---|---|---|---|
| claude-haiku-4-5 | log_probability | 0/500 | 0.000 | 0.000 | — | — | — | — | 0.0000 |
| claude-haiku-4-5 | self_consistency | 500/500 | 0.802 | 0.802 | 0.176 | 0.173 | 0.147 | 0.160 | 0.8540 |
| claude-haiku-4-5 | temperature_0 | 500/500 | 0.810 | 0.810 | 0.190 | 0.190 | 0.176 | 0.187 | 0.1708 |
| claude-haiku-4-5 | verbal_probability | 500/500 | 0.806 | 0.806 | 0.161 | 0.122 | 0.028 | 0.104 | 0.1708 |
| claude-opus-4-7 | log_probability | 0/500 | 0.000 | 0.000 | — | — | — | — | 0.0000 |
| claude-opus-4-7 | self_consistency | 499/500 | 0.930 | 0.930 | 0.068 | 0.067 | 0.049 | 0.060 | 18.7259 |
| claude-opus-4-7 | temperature_0 | 499/500 | 0.932 | 0.932 | 0.066 | 0.066 | 0.051 | 0.062 | 3.7529 |
| claude-opus-4-7 | verbal_probability | 499/500 | 0.930 | 0.930 | 0.089 | 0.069 | 0.032 | 0.049 | 3.7452 |
| deepseek-chat | log_probability | 135/500 | 0.730 | 0.730 | 1.000 | 1.000 | 0.993 | 1.000 | 0.0177 |
| deepseek-chat | self_consistency | 500/500 | 0.716 | 0.716 | 0.211 | 0.218 | 0.202 | 0.240 | 0.0886 |
| deepseek-chat | temperature_0 | 500/500 | 0.728 | 0.728 | 0.272 | 0.272 | 0.254 | 0.260 | 0.0177 |
| deepseek-chat | verbal_probability | 423/500 | 0.724 | 0.724 | 0.273 | 0.251 | 0.085 | 0.228 | 0.0177 |
| gemini-2.5-pro | log_probability | 0/500 | 0.000 | 0.000 | — | — | — | — | 0.0000 |
| gemini-2.5-pro | self_consistency | 500/500 | 0.954 | 0.954 | 0.044 | 0.044 | 0.022 | 0.031 | 0.8747 |
| gemini-2.5-pro | temperature_0 | 500/500 | 0.946 | 0.946 | 0.054 | 0.054 | 0.030 | 0.051 | 0.1749 |
| gemini-2.5-pro | verbal_probability | 500/500 | 0.946 | 0.946 | 0.045 | 0.047 | 0.006 | 0.016 | 0.1750 |
| gpt-5.4-mini | log_probability | 474/500 | 0.786 | 0.786 | 0.148 | 0.170 | 0.302 | 0.171 | 0.0230 |
| gpt-5.4-mini | self_consistency | 500/500 | 0.802 | 0.802 | 0.130 | 0.161 | 0.138 | 0.162 | 0.1152 |
| gpt-5.4-mini | temperature_0 | 500/500 | 0.784 | 0.784 | 0.216 | 0.216 | 0.205 | 0.218 | 0.0230 |
| gpt-5.4-mini | verbal_probability | 500/500 | 0.782 | 0.782 | 0.173 | 0.183 | 0.093 | 0.167 | 0.0230 |

## Model ranking per method (by ECE, lower = better)

### log_probability
1. gpt-5.4-mini — ECE 0.148
2. deepseek-chat — ECE 1.000

### self_consistency
1. gemini-2.5-pro — ECE 0.044
2. claude-opus-4-7 — ECE 0.068
3. gpt-5.4-mini — ECE 0.130
4. claude-haiku-4-5 — ECE 0.176
5. deepseek-chat — ECE 0.211

### temperature_0
1. gemini-2.5-pro — ECE 0.054
2. claude-opus-4-7 — ECE 0.066
3. claude-haiku-4-5 — ECE 0.190
4. gpt-5.4-mini — ECE 0.216
5. deepseek-chat — ECE 0.272

### verbal_probability
1. gemini-2.5-pro — ECE 0.045
2. claude-opus-4-7 — ECE 0.089
3. claude-haiku-4-5 — ECE 0.161
4. gpt-5.4-mini — ECE 0.173
5. deepseek-chat — ECE 0.273

## Ranking stability (Kendall's τ across methods, PROTOCOL §8.2)

| Method pair | Kendall's τ | n_models |
|---|---|---|
| self_consistency vs temperature_0 | 0.800 | 5 |
| self_consistency vs verbal_probability | 0.800 | 5 |
| temperature_0 vs verbal_probability | 1.000 | 5 |

_High τ (> 0.7) = elicitation-invariant ranking. Low τ (< 0.3) = leaderboard is elicitation-dependent (PROTOCOL §12 risk register — publishable outcome either way)._

## Category × difficulty breakdown (accuracy · abstention · ECE per subgroup)

### claude-haiku-4-5 / log_probability
**By category:**
- contraindication: acc=0.000 abst=0.000 ECE=nan n=150
- drug_drug_interaction: acc=0.000 abst=0.000 ECE=nan n=125
- impossible_timing: acc=0.000 abst=0.000 ECE=nan n=100
- physiological_impossibility: acc=0.000 abst=0.000 ECE=nan n=125
**By difficulty:**
- expert: acc=0.000 abst=0.000 ECE=nan n=209
- obvious: acc=0.000 abst=0.000 ECE=nan n=108
- subtle: acc=0.000 abst=0.000 ECE=nan n=183

### claude-haiku-4-5 / self_consistency
**By category:**
- contraindication: acc=0.840 abst=0.840 ECE=0.139 n=150
- drug_drug_interaction: acc=0.736 abst=0.736 ECE=0.227 n=125
- impossible_timing: acc=0.730 abst=0.730 ECE=0.252 n=100
- physiological_impossibility: acc=0.880 abst=0.880 ECE=0.107 n=125
**By difficulty:**
- expert: acc=0.818 abst=0.818 ECE=0.160 n=209
- obvious: acc=0.880 abst=0.880 ECE=0.104 n=108
- subtle: acc=0.738 abst=0.738 ECE=0.236 n=183

### claude-haiku-4-5 / temperature_0
**By category:**
- contraindication: acc=0.847 abst=0.847 ECE=0.153 n=150
- drug_drug_interaction: acc=0.744 abst=0.744 ECE=0.256 n=125
- impossible_timing: acc=0.730 abst=0.730 ECE=0.270 n=100
- physiological_impossibility: acc=0.896 abst=0.896 ECE=0.104 n=125
**By difficulty:**
- expert: acc=0.823 abst=0.823 ECE=0.177 n=209
- obvious: acc=0.889 abst=0.889 ECE=0.111 n=108
- subtle: acc=0.749 abst=0.749 ECE=0.251 n=183

### claude-haiku-4-5 / verbal_probability
**By category:**
- contraindication: acc=0.833 abst=0.833 ECE=0.166 n=150
- drug_drug_interaction: acc=0.744 abst=0.744 ECE=0.222 n=125
- impossible_timing: acc=0.730 abst=0.730 ECE=0.151 n=100
- physiological_impossibility: acc=0.896 abst=0.896 ECE=0.108 n=125
**By difficulty:**
- expert: acc=0.818 abst=0.818 ECE=0.156 n=209
- obvious: acc=0.889 abst=0.889 ECE=0.109 n=108
- subtle: acc=0.743 abst=0.743 ECE=0.198 n=183

### claude-opus-4-7 / log_probability
**By category:**
- contraindication: acc=0.000 abst=0.000 ECE=nan n=150
- drug_drug_interaction: acc=0.000 abst=0.000 ECE=nan n=125
- impossible_timing: acc=0.000 abst=0.000 ECE=nan n=100
- physiological_impossibility: acc=0.000 abst=0.000 ECE=nan n=125
**By difficulty:**
- expert: acc=0.000 abst=0.000 ECE=nan n=209
- obvious: acc=0.000 abst=0.000 ECE=nan n=108
- subtle: acc=0.000 abst=0.000 ECE=nan n=183

### claude-opus-4-7 / self_consistency
**By category:**
- contraindication: acc=0.973 abst=0.973 ECE=0.027 n=150
- drug_drug_interaction: acc=0.904 abst=0.904 ECE=0.094 n=125
- impossible_timing: acc=0.870 abst=0.870 ECE=0.123 n=100
- physiological_impossibility: acc=0.952 abst=0.952 ECE=0.048 n=125
**By difficulty:**
- expert: acc=0.952 abst=0.952 ECE=0.047 n=209
- obvious: acc=0.944 abst=0.944 ECE=0.050 n=108
- subtle: acc=0.896 abst=0.896 ECE=0.103 n=183

### claude-opus-4-7 / temperature_0
**By category:**
- contraindication: acc=0.973 abst=0.973 ECE=0.027 n=150
- drug_drug_interaction: acc=0.904 abst=0.904 ECE=0.096 n=125
- impossible_timing: acc=0.880 abst=0.880 ECE=0.111 n=100
- physiological_impossibility: acc=0.952 abst=0.952 ECE=0.048 n=125
**By difficulty:**
- expert: acc=0.957 abst=0.957 ECE=0.043 n=209
- obvious: acc=0.944 abst=0.944 ECE=0.047 n=108
- subtle: acc=0.896 abst=0.896 ECE=0.104 n=183

### claude-opus-4-7 / verbal_probability
**By category:**
- contraindication: acc=0.973 abst=0.973 ECE=0.104 n=150
- drug_drug_interaction: acc=0.904 abst=0.904 ECE=0.084 n=125
- impossible_timing: acc=0.870 abst=0.870 ECE=0.089 n=100
- physiological_impossibility: acc=0.952 abst=0.952 ECE=0.084 n=125
**By difficulty:**
- expert: acc=0.952 abst=0.952 ECE=0.117 n=209
- obvious: acc=0.944 abst=0.944 ECE=0.070 n=108
- subtle: acc=0.896 abst=0.896 ECE=0.082 n=183

### deepseek-chat / log_probability
**By category:**
- contraindication: acc=0.793 abst=0.793 ECE=1.000 n=150
- drug_drug_interaction: acc=0.712 abst=0.712 ECE=1.000 n=125
- impossible_timing: acc=0.530 abst=0.530 ECE=1.000 n=100
- physiological_impossibility: acc=0.832 abst=0.832 ECE=1.000 n=125
**By difficulty:**
- expert: acc=0.746 abst=0.746 ECE=1.000 n=209
- obvious: acc=0.778 abst=0.778 ECE=1.000 n=108
- subtle: acc=0.683 abst=0.683 ECE=1.000 n=183

### deepseek-chat / self_consistency
**By category:**
- contraindication: acc=0.787 abst=0.787 ECE=0.159 n=150
- drug_drug_interaction: acc=0.688 abst=0.688 ECE=0.227 n=125
- impossible_timing: acc=0.520 abst=0.520 ECE=0.392 n=100
- physiological_impossibility: acc=0.816 abst=0.816 ECE=0.114 n=125
**By difficulty:**
- expert: acc=0.737 abst=0.737 ECE=0.189 n=209
- obvious: acc=0.759 abst=0.759 ECE=0.196 n=108
- subtle: acc=0.667 abst=0.667 ECE=0.245 n=183

### deepseek-chat / temperature_0
**By category:**
- contraindication: acc=0.800 abst=0.800 ECE=0.200 n=150
- drug_drug_interaction: acc=0.696 abst=0.696 ECE=0.304 n=125
- impossible_timing: acc=0.530 abst=0.530 ECE=0.470 n=100
- physiological_impossibility: acc=0.832 abst=0.832 ECE=0.168 n=125
**By difficulty:**
- expert: acc=0.742 abst=0.742 ECE=0.258 n=209
- obvious: acc=0.778 abst=0.778 ECE=0.222 n=108
- subtle: acc=0.683 abst=0.683 ECE=0.317 n=183

### deepseek-chat / verbal_probability
**By category:**
- contraindication: acc=0.793 abst=0.793 ECE=0.211 n=150
- drug_drug_interaction: acc=0.688 abst=0.688 ECE=0.292 n=125
- impossible_timing: acc=0.530 abst=0.530 ECE=0.461 n=100
- physiological_impossibility: acc=0.832 abst=0.832 ECE=0.179 n=125
**By difficulty:**
- expert: acc=0.742 abst=0.742 ECE=0.259 n=209
- obvious: acc=0.769 abst=0.769 ECE=0.241 n=108
- subtle: acc=0.678 abst=0.678 ECE=0.307 n=183

### gemini-2.5-pro / log_probability
**By category:**
- contraindication: acc=0.000 abst=0.000 ECE=nan n=150
- drug_drug_interaction: acc=0.000 abst=0.000 ECE=nan n=125
- impossible_timing: acc=0.000 abst=0.000 ECE=nan n=100
- physiological_impossibility: acc=0.000 abst=0.000 ECE=nan n=125
**By difficulty:**
- expert: acc=0.000 abst=0.000 ECE=nan n=209
- obvious: acc=0.000 abst=0.000 ECE=nan n=108
- subtle: acc=0.000 abst=0.000 ECE=nan n=183

### gemini-2.5-pro / self_consistency
**By category:**
- contraindication: acc=0.993 abst=0.993 ECE=0.013 n=150
- drug_drug_interaction: acc=0.912 abst=0.912 ECE=0.085 n=125
- impossible_timing: acc=0.950 abst=0.950 ECE=0.050 n=100
- physiological_impossibility: acc=0.952 abst=0.952 ECE=0.037 n=125
**By difficulty:**
- expert: acc=0.971 abst=0.971 ECE=0.031 n=209
- obvious: acc=0.981 abst=0.981 ECE=0.022 n=108
- subtle: acc=0.918 abst=0.918 ECE=0.078 n=183

### gemini-2.5-pro / temperature_0
**By category:**
- contraindication: acc=0.993 abst=0.993 ECE=0.007 n=150
- drug_drug_interaction: acc=0.920 abst=0.920 ECE=0.080 n=125
- impossible_timing: acc=0.930 abst=0.930 ECE=0.070 n=100
- physiological_impossibility: acc=0.928 abst=0.928 ECE=0.072 n=125
**By difficulty:**
- expert: acc=0.962 abst=0.962 ECE=0.038 n=209
- obvious: acc=0.972 abst=0.972 ECE=0.028 n=108
- subtle: acc=0.913 abst=0.913 ECE=0.087 n=183

### gemini-2.5-pro / verbal_probability
**By category:**
- contraindication: acc=0.993 abst=0.993 ECE=0.003 n=150
- drug_drug_interaction: acc=0.920 abst=0.920 ECE=0.070 n=125
- impossible_timing: acc=0.930 abst=0.930 ECE=0.053 n=100
- physiological_impossibility: acc=0.928 abst=0.928 ECE=0.063 n=125
**By difficulty:**
- expert: acc=0.962 abst=0.962 ECE=0.027 n=209
- obvious: acc=0.972 abst=0.972 ECE=0.021 n=108
- subtle: acc=0.913 abst=0.913 ECE=0.079 n=183

### gpt-5.4-mini / log_probability
**By category:**
- contraindication: acc=0.933 abst=0.933 ECE=0.056 n=150
- drug_drug_interaction: acc=0.792 abst=0.792 ECE=0.150 n=125
- impossible_timing: acc=0.600 abst=0.600 ECE=0.337 n=100
- physiological_impossibility: acc=0.752 abst=0.752 ECE=0.197 n=125
**By difficulty:**
- expert: acc=0.785 abst=0.785 ECE=0.159 n=209
- obvious: acc=0.852 abst=0.852 ECE=0.150 n=108
- subtle: acc=0.749 abst=0.749 ECE=0.181 n=183

### gpt-5.4-mini / self_consistency
**By category:**
- contraindication: acc=0.920 abst=0.920 ECE=0.075 n=150
- drug_drug_interaction: acc=0.824 abst=0.824 ECE=0.112 n=125
- impossible_timing: acc=0.680 abst=0.680 ECE=0.220 n=100
- physiological_impossibility: acc=0.736 abst=0.736 ECE=0.190 n=125
**By difficulty:**
- expert: acc=0.813 abst=0.813 ECE=0.138 n=209
- obvious: acc=0.833 abst=0.833 ECE=0.111 n=108
- subtle: acc=0.770 abst=0.770 ECE=0.137 n=183

### gpt-5.4-mini / temperature_0
**By category:**
- contraindication: acc=0.913 abst=0.913 ECE=0.087 n=150
- drug_drug_interaction: acc=0.768 abst=0.768 ECE=0.232 n=125
- impossible_timing: acc=0.630 abst=0.630 ECE=0.370 n=100
- physiological_impossibility: acc=0.768 abst=0.768 ECE=0.232 n=125
**By difficulty:**
- expert: acc=0.794 abst=0.794 ECE=0.206 n=209
- obvious: acc=0.843 abst=0.843 ECE=0.157 n=108
- subtle: acc=0.738 abst=0.738 ECE=0.262 n=183

### gpt-5.4-mini / verbal_probability
**By category:**
- contraindication: acc=0.893 abst=0.893 ECE=0.077 n=150
- drug_drug_interaction: acc=0.824 abst=0.824 ECE=0.127 n=125
- impossible_timing: acc=0.640 abst=0.640 ECE=0.303 n=100
- physiological_impossibility: acc=0.720 abst=0.720 ECE=0.230 n=125
**By difficulty:**
- expert: acc=0.799 abst=0.799 ECE=0.150 n=209
- obvious: acc=0.843 abst=0.843 ECE=0.127 n=108
- subtle: acc=0.727 abst=0.727 ECE=0.226 n=183

