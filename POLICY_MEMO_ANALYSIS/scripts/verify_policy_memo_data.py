"""
COMPREHENSIVE POLICY MEMO DATA VERIFICATION SCRIPT
Computes ALL statistics, numbers, and data referenced in the MIT Hackathon Policy Memo

IMPORTANT: All analyses focus on PASSED, CHILDREN-RELATED bills only.

Author: MIT Hackathon Policy Team
Date: November 22, 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from collections import Counter, defaultdict
import re
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['figure.figsize'] = (12, 8)

class PolicyMemoDataVerification:
    """
    Comprehensive data verification and computation for policy memo.
    All numbers in the memo must be traceable to methods in this class.
    
    CRITICAL: All analyses use PASSED, CHILDREN-RELATED bills only.
    """
    
    def __init__(self, state_file, federal_file, output_dir=None):
        """Initialize with data files"""
        print("="*80)
        print("MIT HACKATHON POLICY MEMO - DATA VERIFICATION SCRIPT")
        print("="*80)
        print("\nLoading data files...")
        
        self.state_df = pd.read_csv(state_file, encoding='utf-8', low_memory=False)
        self.federal_df = pd.read_csv(federal_file, encoding='utf-8', low_memory=False)
        
        print(f"✓ Loaded {len(self.state_df):,} total state bills")
        print(f"✓ Loaded {len(self.federal_df):,} total federal bills")
        print(f"✓ Total bills in dataset: {len(self.state_df) + len(self.federal_df):,}")
        
        # Create output directory
        if output_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = f"HACKATHON_DELIVERABLES/data/memo_verification_{timestamp}"
        
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(f"{self.output_dir}/visualizations", exist_ok=True)
        
        # Initialize storage for all computed statistics
        self.stats = {}
        self.methodology = {}
        
        # Filter for PASSED bills first
        print("\n" + "="*80)
        print("FILTERING FOR PASSED BILLS")
        print("="*80)
        self.passed_state_df = self.state_df[
            self.state_df['Status'].str.contains('Passed', na=False, case=False)
        ]
        print(f"✓ Passed state bills: {len(self.passed_state_df):,} ({len(self.passed_state_df)/len(self.state_df)*100:.1f}%)")
        
        # Filter for CHILDREN-RELATED bills
        print("\n" + "="*80)
        print("FILTERING FOR CHILDREN-RELATED BILLS")
        print("="*80)
        self.children_bills = self._filter_children_related_bills(self.passed_state_df)
        print(f"✓ Children-related passed bills: {len(self.children_bills):,} ({len(self.children_bills)/len(self.passed_state_df)*100:.1f}%)")
        
        print(f"\n✓ Output directory: {self.output_dir}\n")
    
    def _filter_children_related_bills(self, df):
        """
        Filter for children-related bills using comprehensive keyword matching.
        This is the CORE filter applied to all analyses.
        """
        children_keywords = [
            'child', 'children', 'minor', 'minors', 'youth', 'student', 'students',
            'teen', 'teenager', 'teenagers', 'kid', 'kids', 'adolescent', 'adolescents',
            'juvenile', 'juveniles', 'parental', 'parent', 'parents', 'guardian', 
            'guardians', 'family', 'young people', 'underage', 'under age',
            'k-12', 'k12', 'school', 'schools', 'classroom'
        ]
        
        # Also include online safety keywords that typically relate to children
        online_safety_keywords = [
            'online safety', 'internet safety', 'social media', 
            'age verification', 'age appropriate', 'age-appropriate',
            'digital literacy', 'digital citizenship'
        ]
        
        all_keywords = children_keywords + online_safety_keywords
        
        # Create comprehensive mask
        mask = pd.Series([False] * len(df), index=df.index)
        
        for keyword in all_keywords:
            mask |= (
                df['Name'].str.contains(keyword, case=False, na=False, regex=False) |
                df['Description'].str.contains(keyword, case=False, na=False, regex=False) |
                df['Themes'].str.contains(keyword, case=False, na=False, regex=False)
            )
        
        filtered_df = df[mask].copy()
        
        print(f"  ✓ Keywords matched: {len(all_keywords)} patterns")
        print(f"  ✓ Bills matched: {len(filtered_df):,}")
        
        return filtered_df
    
    def compute_all_statistics(self):
        """Master function that computes ALL statistics for the policy memo"""
        print("\n" + "="*80)
        print("COMPUTING ALL POLICY MEMO STATISTICS")
        print("="*80)
        print("NOTE: All statistics based on PASSED, CHILDREN-RELATED bills only\n")
        
        # 1. Dataset Overview
        self.compute_dataset_overview()
        
        # 2. Geographic Inequity Analysis
        self.compute_geographic_inequity()
        
        # 3. State Consensus Analysis (provision adoption rates)
        self.compute_state_consensus()
        
        # 4. Federal Inaction Metrics
        self.compute_federal_inaction()
        
        # 5. Legislative Momentum
        self.compute_legislative_momentum()
        
        # 6. Evidence Gap Analysis
        self.compute_evidence_gaps()
        
        # 7. Compliance Complexity
        self.compute_compliance_complexity()
        
        # Generate final report
        self.generate_comprehensive_report()
        
        print("\n" + "="*80)
        print("VERIFICATION COMPLETE")
        print("="*80)
        print(f"\nAll results saved to: {self.output_dir}")
        print(f"See 'COMPREHENSIVE_MEMO_STATISTICS.txt' for full report")
    
    def compute_dataset_overview(self):
        """
        MEMO CLAIM: "Analysis of 7,938 state and federal bills since 2020"
        METHODOLOGY: Count total bills, then filter to passed children-related bills
        """
        print("▶ Computing Dataset Overview Statistics...")
        
        # Total bills (all)
        total_state = len(self.state_df)
        total_federal = len(self.federal_df)
        total_bills = total_state + total_federal
        
        # Passed bills
        total_passed_state = len(self.passed_state_df)
        
        # Children-related passed bills (our analysis focus)
        total_children_passed = len(self.children_bills)
        
        self.stats['total_bills'] = total_bills
        self.stats['total_state_bills'] = total_state
        self.stats['total_federal_bills'] = total_federal
        self.stats['total_passed_state_bills'] = total_passed_state
        self.stats['total_children_passed_bills'] = total_children_passed
        
        # Date range analysis
        self.children_bills['status_date_parsed'] = pd.to_datetime(
            self.children_bills['status_date'], errors='coerce'
        )
        self.children_bills['intro_date_parsed'] = pd.to_datetime(
            self.children_bills['Intro Date'], format='%d/%m/%Y', errors='coerce'
        )
        
        # Get date range
        valid_dates = pd.concat([
            self.children_bills['status_date_parsed'].dropna(),
            self.children_bills['intro_date_parsed'].dropna()
        ])
        
        if len(valid_dates) > 0:
            min_date = valid_dates.min()
            max_date = valid_dates.max()
            self.stats['date_range_start'] = min_date.strftime('%Y-%m-%d')
            self.stats['date_range_end'] = max_date.strftime('%Y-%m-%d')
        
        self.methodology['dataset_overview'] = f"""
DATASET OVERVIEW METHODOLOGY:
- Total bills in dataset = State bills ({total_state:,}) + Federal bills ({total_federal:,}) = {total_bills:,}
- Passed state bills: {total_passed_state:,} ({total_passed_state/total_state*100:.1f}% of state bills)
- Children-related passed bills (ANALYSIS FOCUS): {total_children_passed:,} ({total_children_passed/total_passed_state*100:.1f}% of passed bills)
- Date range (children-related passed bills): {self.stats.get('date_range_start', 'N/A')} to {self.stats.get('date_range_end', 'N/A')}

CRITICAL FILTER APPLIED:
All subsequent analyses use ONLY the {total_children_passed:,} bills that are:
1. PASSED (enacted into law)
2. CHILDREN-RELATED (contain keywords related to minors, youth, online safety, etc.)

Data source: Integrity Institute Technology Policy Legislative Tracker
"""
        
        print(f"  ✓ Total bills in dataset: {total_bills:,}")
        print(f"  ✓ Passed state bills: {total_passed_state:,}")
        print(f"  ✓ Children-related passed bills (ANALYSIS FOCUS): {total_children_passed:,}")
        print(f"  ✓ Date range: {self.stats.get('date_range_start', 'N/A')} to {self.stats.get('date_range_end', 'N/A')}\n")
    
    def compute_geographic_inequity(self):
        """
        MEMO CLAIMS:
        - "52% live in states with minimal safeguards"
        - "19% benefit from comprehensive regulation"
        - "Geographic Inequity Index of 2.06"
        
        METHODOLOGY: Score each state by number of unique provisions implemented
        NOTE: Uses ONLY passed, children-related bills
        """
        print("▶ Computing Geographic Inequity Statistics...")
        print("  (Using PASSED, CHILDREN-RELATED bills only)")
        
        # Use the already-filtered children_bills
        children_bills = self.children_bills
        
        # Define 8 key provisions for scoring states
        provisions = {
            'transparency_reporting': [
                'transparency report', 'disclosure', 'annual report', 
                'transparency', 'reporting requirement', 'public report'
            ],
            'digital_literacy_education': [
                'digital literacy', 'digital citizenship', 'education', 
                'training', 'awareness program', 'curriculum', 'digital wellness'
            ],
            'data_privacy_standards': [
                'data privacy', 'data protection', 'personal data', 
                'privacy by design', 'data minimization', 'privacy standard',
                'data collection', 'privacy policy'
            ],
            'platform_liability': [
                'liability', 'duty of care', 'negligent', 'civil action',
                'damages', 'responsible', 'accountable', 'liable'
            ],
            'age_verification': [
                'age verification', 'age assurance', 'age check', 
                'verify age', 'age gate', 'age authentication', 'verify identity'
            ],
            'mental_health_protections': [
                'mental health', 'addiction', 'addictive', 'wellness',
                'psychological', 'self-harm', 'suicide', 'depression',
                'well-being', 'wellbeing'
            ],
            'content_safety_standards': [
                'content moderation', 'content safety', 'harmful content',
                'filter', 'content standard', 'inappropriate content',
                'content removal'
            ],
            'parental_control_tools': [
                'parental control', 'parental consent', 'parent approval',
                'guardian consent', 'parental dashboard', 'parent access',
                'parental notification', 'parental rights'
            ]
        }
        
        # Score each state based on provisions present
        state_scores = {}
        state_provisions = {}
        state_laws = {}
        
        for state in children_bills['State'].unique():
            state_bills = children_bills[children_bills['State'] == state]
            score = 0
            provisions_present = []
            laws_implementing = []
            
            for prov_name, keywords in provisions.items():
                provision_found = False
                for keyword in keywords:
                    matching_bills = state_bills[
                        state_bills['Description'].str.contains(keyword, case=False, na=False, regex=False)
                    ]
                    if not matching_bills.empty:
                        score += 1
                        provisions_present.append(prov_name)
                        provision_found = True
                        
                        # Record laws implementing this provision
                        for _, bill in matching_bills.head(3).iterrows():
                            laws_implementing.append({
                                'provision': prov_name,
                                'law': bill['Name'],
                                'state': state
                            })
                        break
                
            state_scores[state] = score
            state_provisions[state] = provisions_present
            state_laws[state] = laws_implementing
        
        # Calculate distribution statistics
        all_scores = list(state_scores.values())
        total_states = len(all_scores)
        
        # Define tiers
        low_protection = sum(1 for s in all_scores if s <= 3)
        medium_protection = sum(1 for s in all_scores if 4 <= s <= 5)
        high_protection = sum(1 for s in all_scores if s >= 6)
        
        # Calculate percentages
        pct_low = (low_protection / total_states * 100) if total_states > 0 else 0
        pct_medium = (medium_protection / total_states * 100) if total_states > 0 else 0
        pct_high = (high_protection / total_states * 100) if total_states > 0 else 0
        
        # Geographic Inequity Index
        mean_score = np.mean(all_scores)
        std_score = np.std(all_scores)
        gii_cv = std_score / mean_score if mean_score > 0 else 0
        gii_std = std_score
        
        self.stats['geographic_inequity'] = {
            'total_states_analyzed': total_states,
            'low_protection_states': low_protection,
            'medium_protection_states': medium_protection,
            'high_protection_states': high_protection,
            'pct_low_protection': pct_low,
            'pct_medium_protection': pct_medium,
            'pct_high_protection': pct_high,
            'mean_protection_score': mean_score,
            'std_protection_score': std_score,
            'geographic_inequity_index_cv': gii_cv,
            'geographic_inequity_index_std': gii_std,
            'min_score': min(all_scores) if all_scores else 0,
            'max_score': max(all_scores) if all_scores else 0,
            'state_scores': state_scores,
            'state_provisions': state_provisions
        }
        
        # Save detailed state scores
        state_scores_df = pd.DataFrame([
            {
                'State': state,
                'Protection_Score': score,
                'Tier': 'High (6-8)' if score >= 6 else 'Medium (4-5)' if score >= 4 else 'Low (0-3)',
                'Provisions_Count': len(state_provisions.get(state, [])),
                'Provisions': ', '.join(state_provisions.get(state, [])),
                'Example_Laws': ' | '.join([f"{law['law']}" for law in state_laws.get(state, [])[:3]])
            }
            for state, score in sorted(state_scores.items(), key=lambda x: x[1], reverse=True)
        ])
        state_scores_df.to_csv(f"{self.output_dir}/state_protection_scores.csv", index=False)
        
        # Create visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Bar chart of top states
        sorted_states = sorted(state_scores.items(), key=lambda x: x[1], reverse=True)[:20]
        states = [s[0] for s in sorted_states]
        scores = [s[1] for s in sorted_states]
        
        colors = ['#27ae60' if s >= 6 else '#f39c12' if s >= 4 else '#e74c3c' for s in scores]
        ax1.barh(states, scores, color=colors, edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Protection Score (0-8 provisions)', fontweight='bold', fontsize=12)
        ax1.set_title('State Protection Scores (Top 20)\nGeographic Inequity Analysis',
                     fontweight='bold', fontsize=13)
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()
        
        for i, (state, score) in enumerate(sorted_states):
            ax1.text(score + 0.1, i, str(score), va='center', fontweight='bold')
        
        # Pie chart of distribution
        tier_data = [high_protection, medium_protection, low_protection]
        tier_labels = [
            f'High Protection\n6-8 provisions\n{pct_high:.0f}%',
            f'Medium Protection\n4-5 provisions\n{pct_medium:.0f}%',
            f'Low Protection\n0-3 provisions\n{pct_low:.0f}%'
        ]
        colors_pie = ['#27ae60', '#f39c12', '#e74c3c']
        
        wedges, texts, autotexts = ax2.pie(
            tier_data, labels=tier_labels, autopct='%1.0f%%',
            colors=colors_pie, startangle=90, textprops={'fontweight': 'bold', 'fontsize': 11}
        )
        ax2.set_title('Distribution of State Protection Levels\nMost Children Live in Low-Protection States',
                     fontweight='bold', fontsize=13)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/visualizations/geographic_inequity_analysis.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        self.methodology['geographic_inequity'] = f"""
GEOGRAPHIC INEQUITY METHODOLOGY:
- Data source: {len(children_bills):,} PASSED, CHILDREN-RELATED state bills
- Analyzed {total_states} states with children's online safety legislation
- Scored each state on 8 key provisions (0-8 scale):
  1. Transparency & Reporting
  2. Digital Literacy Education
  3. Data Privacy Standards
  4. Platform Liability
  5. Age Verification
  6. Mental Health Protections
  7. Content Safety Standards
  8. Parental Control Tools

- Classification:
  * Low Protection (0-3 provisions): {low_protection} states ({pct_low:.1f}%)
  * Medium Protection (4-5 provisions): {medium_protection} states ({pct_medium:.1f}%)
  * High Protection (6-8 provisions): {high_protection} states ({pct_high:.1f}%)

- Geographic Inequity Index (GII):
  * Standard Deviation: {gii_std:.2f}
  * Coefficient of Variation: {gii_cv:.2f}

- Score Distribution:
  * Mean: {mean_score:.2f}
  * Std Dev: {std_score:.2f}
  * Min: {min(all_scores) if all_scores else 0}
  * Max: {max(all_scores) if all_scores else 0}
"""
        
        print(f"  ✓ States analyzed: {total_states}")
        print(f"  ✓ Low protection (0-3): {low_protection} states ({pct_low:.0f}%)")
        print(f"  ✓ Medium protection (4-5): {medium_protection} states ({pct_medium:.0f}%)")
        print(f"  ✓ High protection (6-8): {high_protection} states ({pct_high:.0f}%)")
        print(f"  ✓ Geographic Inequity Index: {gii_std:.2f}\n")
    
    def compute_state_consensus(self):
        """
        MEMO CLAIMS: State consensus percentages for each provision
        METHODOLOGY: Calculate percentage of states that have enacted each provision
        NOTE: Uses ONLY passed, children-related bills
        """
        print("▶ Computing State Consensus (Provision Adoption Rates)...")
        print("  (Using PASSED, CHILDREN-RELATED bills only)")
        
        if 'geographic_inequity' not in self.stats:
            self.compute_geographic_inequity()
        
        state_provisions = self.stats['geographic_inequity']['state_provisions']
        total_states = self.stats['geographic_inequity']['total_states_analyzed']
        
        # Count provisions
        provision_counts = defaultdict(int)
        provision_states = defaultdict(list)
        
        for state, provisions in state_provisions.items():
            for prov in provisions:
                provision_counts[prov] += 1
                provision_states[prov].append(state)
        
        # Calculate percentages
        provision_percentages = {}
        provision_mapping = {
            'transparency_reporting': 'Transparency & Reporting',
            'digital_literacy_education': 'Digital Literacy Education',
            'data_privacy_standards': 'Data Privacy Standards',
            'platform_liability': 'Platform Liability',
            'age_verification': 'Age Verification',
            'mental_health_protections': 'Mental Health Protections',
            'content_safety_standards': 'Content Safety Standards',
            'parental_control_tools': 'Parental Control Tools'
        }
        
        for prov_key, prov_name in provision_mapping.items():
            count = provision_counts.get(prov_key, 0)
            percentage = (count / total_states * 100) if total_states > 0 else 0
            provision_percentages[prov_name] = {
                'count': count,
                'percentage': percentage,
                'states': provision_states.get(prov_key, [])
            }
        
        self.stats['state_consensus'] = provision_percentages
        
        # Create table
        consensus_df = pd.DataFrame([
            {
                'Provision': prov_name,
                'States_Adopted': data['count'],
                'Percentage': f"{data['percentage']:.1f}%",
                'Adoption_Level': 'High Consensus (>50%)' if data['percentage'] >= 50 else 'Moderate Consensus (25-50%)' if data['percentage'] >= 25 else 'Low Consensus (<25%)',
                'Example_States': ', '.join(data['states'][:5])
            }
            for prov_name, data in sorted(provision_percentages.items(), 
                                         key=lambda x: x[1]['percentage'], reverse=True)
        ])
        consensus_df.to_csv(f"{self.output_dir}/state_consensus_provisions.csv", index=False)
        
        # Create visualization
        fig, ax = plt.subplots(figsize=(14, 8))
        
        sorted_provisions = sorted(provision_percentages.items(), 
                                  key=lambda x: x[1]['percentage'], reverse=True)
        prov_names = [p[0] for p in sorted_provisions]
        prov_pcts = [p[1]['percentage'] for p in sorted_provisions]
        prov_counts = [p[1]['count'] for p in sorted_provisions]
        
        colors = ['#27ae60' if p >= 50 else '#f39c12' if p >= 25 else '#e74c3c' for p in prov_pcts]
        
        bars = ax.barh(prov_names, prov_pcts, color=colors, edgecolor='black', alpha=0.8)
        ax.set_xlabel('Percentage of States Adopting Provision', fontweight='bold', fontsize=12)
        ax.set_title('State Consensus on Key Provisions\nAdoption Rates Across States',
                    fontweight='bold', fontsize=13)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
        
        for i, (pct, count) in enumerate(zip(prov_pcts, prov_counts)):
            ax.text(pct + 1, i, f'{pct:.0f}% ({count} states)', 
                   va='center', fontweight='bold', fontsize=10)
        
        ax.axvline(x=50, color='green', linestyle='--', alpha=0.5, linewidth=2, label='High Consensus (50%+)')
        ax.axvline(x=25, color='orange', linestyle='--', alpha=0.5, linewidth=2, label='Moderate Consensus (25%+)')
        ax.legend(fontsize=10, loc='lower right')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/visualizations/state_consensus_analysis.png", 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
        self.methodology['state_consensus'] = f"""
STATE CONSENSUS METHODOLOGY:
- Analyzed {total_states} states with passed children's online safety legislation
- Calculated percentage of states that have enacted each provision

Provision Adoption Rates:
"""
        for prov_name, data in sorted(provision_percentages.items(), 
                                     key=lambda x: x[1]['percentage'], reverse=True):
            self.methodology['state_consensus'] += f"  * {prov_name}: {data['count']}/{total_states} states ({data['percentage']:.1f}%)\n"
        
        print(f"  ✓ Provisions analyzed: 8 key provisions")
        print(f"  ✓ Highest: {sorted_provisions[0][0]} ({sorted_provisions[0][1]['percentage']:.0f}%)")
        print(f"  ✓ Lowest: {sorted_provisions[-1][0]} ({sorted_provisions[-1][1]['percentage']:.0f}%)\n")
    
    def compute_federal_inaction(self):
        """Federal vs state action metrics"""
        print("▶ Computing Federal Inaction Metrics...")
        
        total_passed_children_state = len(self.children_bills)
        
        # Federal bills
        children_keywords = [
            'child', 'children', 'minor', 'minors', 'youth', 'student',
            'teen', 'teenager', 'kid', 'kids', 'adolescent', 'juvenile',
            'parental', 'parent', 'online safety', 'COPPA', 'KOSA'
        ]
        
        federal_mask = pd.Series([False] * len(self.federal_df), index=self.federal_df.index)
        for keyword in children_keywords:
            federal_mask |= (
                self.federal_df['Name'].str.contains(keyword, case=False, na=False, regex=False) |
                self.federal_df.get('Description', pd.Series([''] * len(self.federal_df))).str.contains(keyword, case=False, na=False, regex=False)
            )
        
        federal_children = self.federal_df[federal_mask]
        
        if 'Status' in self.federal_df.columns:
            federal_passed = federal_children[
                federal_children['Status'].str.contains('Enacted|Passed|Became Law', na=False, case=False, regex=True)
            ]
        else:
            federal_passed = pd.DataFrame()
        
        federal_passed_count = len(federal_passed)
        ratio = total_passed_children_state / federal_passed_count if federal_passed_count > 0 else total_passed_children_state
        
        # 2025 introductions
        self.state_df['Intro_Year'] = pd.to_datetime(
            self.state_df['Intro Date'], format='%d/%m/%Y', errors='coerce'
        ).dt.year
        bills_2025 = len(self.state_df[self.state_df['Intro_Year'] == 2025])
        
        if 'geographic_inequity' in self.stats:
            state_scores = list(self.stats['geographic_inequity']['state_scores'].values())
            avg_requirements = np.mean(state_scores)
            std_requirements = np.std(state_scores)
        else:
            avg_requirements = 0
            std_requirements = 0
        
        num_regimes = len(self.stats['geographic_inequity']['state_scores']) if 'geographic_inequity' in self.stats else 0
        
        self.stats['federal_inaction'] = {
            'state_bills_passed': total_passed_children_state,
            'federal_bills_passed': federal_passed_count,
            'state_federal_ratio': ratio,
            'bills_introduced_2025': bills_2025,
            'avg_requirements_per_state': avg_requirements,
            'std_requirements_per_state': std_requirements,
            'number_of_compliance_regimes': num_regimes
        }
        
        self.methodology['federal_inaction'] = f"""
FEDERAL INACTION METHODOLOGY:
- State bills passed (children-related): {total_passed_children_state}
- Federal bills passed (children-related): {federal_passed_count}
- State-to-Federal ratio: {ratio:.0f}:1
- Bills introduced in 2025: {bills_2025:,}
- Compliance regimes: {num_regimes}
- Avg requirements/state: {avg_requirements:.2f}
- Std deviation: {std_requirements:.2f}
"""
        
        print(f"  ✓ State bills: {total_passed_children_state}")
        print(f"  ✓ Federal bills: {federal_passed_count}")
        print(f"  ✓ Ratio: {ratio:.0f}:1\n")
    
    def compute_legislative_momentum(self):
        """Temporal trends"""
        print("▶ Computing Legislative Momentum...")
        
        bills_2025 = self.stats['federal_inaction']['bills_introduced_2025']
        
        if 'geographic_inequity' in self.stats:
            comprehensive_states = self.stats['geographic_inequity']['high_protection_states']
        else:
            comprehensive_states = 0
        
        self.children_bills['Intro_Year'] = pd.to_datetime(
            self.children_bills['Intro Date'], format='%d/%m/%Y', errors='coerce'
        ).dt.year
        
        yearly_counts = self.children_bills.groupby('Intro_Year').size()
        yearly_counts = yearly_counts[yearly_counts.index.notna()].sort_index()
        
        self.stats['legislative_momentum'] = {
            'bills_introduced_2025': bills_2025,
            'comprehensive_framework_states': comprehensive_states,
            'yearly_passed_bills': yearly_counts.to_dict()
        }
        
        self.methodology['legislative_momentum'] = f"""
LEGISLATIVE MOMENTUM:
- 2025 bills introduced: {bills_2025:,}
- Comprehensive frameworks: {comprehensive_states} states
"""
        
        print(f"  ✓ 2025 bills: {bills_2025:,}")
        print(f"  ✓ Comprehensive states: {comprehensive_states}\n")
    
    def compute_evidence_gaps(self):
        """Evidence gap analysis"""
        print("▶ Computing Evidence Gaps...")
        
        sample_size = min(500, len(self.children_bills))
        sample_df = self.children_bills.sample(n=sample_size, random_state=42) if len(self.children_bills) > 0 else pd.DataFrame()
        
        evidence_keywords = {
            'privacy_data': ['study', 'research', 'data show', 'evidence', 'analysis'],
            'impact_data': ['efficacy', 'effectiveness', 'outcome', 'result'],
            'cost_data': ['cost', 'economic impact', 'fiscal', 'budget'],
            'verification_efficacy': ['verification accuracy', 'false positive']
        }
        
        evidence_counts = {}
        for evidence_type, keywords in evidence_keywords.items():
            count = 0
            for _, bill in sample_df.iterrows():
                desc = str(bill['Description']).lower()
                if any(kw.lower() in desc for kw in keywords):
                    count += 1
            evidence_counts[f'{evidence_type}_pct'] = (count / sample_size * 100) if sample_size > 0 else 0
        
        bills_with_any_evidence = 0
        for _, bill in sample_df.iterrows():
            desc = str(bill['Description']).lower()
            has_evidence = any(
                any(kw.lower() in desc for kw in keywords)
                for keywords in evidence_keywords.values()
            )
            if has_evidence:
                bills_with_any_evidence += 1
        
        evidence_gap_pct = ((sample_size - bills_with_any_evidence) / sample_size * 100) if sample_size > 0 else 0
        
        self.stats['evidence_gaps'] = {
            'sample_size': sample_size,
            'bills_with_evidence': bills_with_any_evidence,
            'evidence_gap_percentage': evidence_gap_pct,
            'privacy_data_gap': 100 - evidence_counts['privacy_data_pct'],
            'impact_data_gap': 100 - evidence_counts['impact_data_pct'],
            'cost_data_gap': 100 - evidence_counts['cost_data_pct']
        }
        
        self.methodology['evidence_gaps'] = f"""
EVIDENCE GAP METHODOLOGY:
- Sampled {sample_size} bills
- Evidence gap: {evidence_gap_pct:.1f}%
- Privacy data gap: {self.stats['evidence_gaps']['privacy_data_gap']:.1f}%
- Impact data gap: {self.stats['evidence_gaps']['impact_data_gap']:.1f}%
- Cost data gap: {self.stats['evidence_gaps']['cost_data_gap']:.1f}%
"""
        
        print(f"  ✓ Sample: {sample_size}")
        print(f"  ✓ Evidence gap: {evidence_gap_pct:.1f}%\n")
    
    def compute_compliance_complexity(self):
        """Compliance complexity"""
        print("▶ Computing Compliance Complexity...")
        
        if 'geographic_inequity' not in self.stats:
            self.compute_geographic_inequity()
        
        state_scores = self.stats['geographic_inequity']['state_scores']
        num_regimes = len(state_scores)
        
        scores_list = list(state_scores.values())
        avg_requirements = np.mean(scores_list) if scores_list else 0
        std_requirements = np.std(scores_list) if scores_list else 0
        
        self.stats['compliance_complexity'] = {
            'number_of_regimes': num_regimes,
            'avg_requirements': avg_requirements,
            'std_requirements': std_requirements
        }
        
        self.methodology['compliance_complexity'] = f"""
COMPLIANCE COMPLEXITY:
- Number of regimes: {num_regimes}
- Avg requirements: {avg_requirements:.2f}
- Std deviation: {std_requirements:.2f}
"""
        
        print(f"  ✓ Regimes: {num_regimes}")
        print(f"  ✓ Avg requirements: {avg_requirements:.2f}\n")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive report"""
        print("▶ Generating Report...")
        
        report_lines = []
        report_lines.append("="*80)
        report_lines.append("MIT HACKATHON POLICY MEMO - DATA VERIFICATION REPORT")
        report_lines.append("="*80)
        report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("\nCRITICAL: ALL ANALYSES USE PASSED, CHILDREN-RELATED BILLS ONLY\n")
        
        report_lines.append("="*80)
        report_lines.append("KEY STATISTICS")
        report_lines.append("="*80)
        
        report_lines.append(f"\n📊 DATASET:")
        report_lines.append(f"   Total bills: {self.stats['total_bills']:,}")
        report_lines.append(f"   Passed state bills: {self.stats['total_passed_state_bills']:,}")
        report_lines.append(f"   Children-related passed: {self.stats['total_children_passed_bills']:,}")
        
        gi = self.stats['geographic_inequity']
        report_lines.append(f"\n📍 GEOGRAPHIC INEQUITY:")
        report_lines.append(f"   Low: {gi['low_protection_states']} ({gi['pct_low_protection']:.0f}%)")
        report_lines.append(f"   Medium: {gi['medium_protection_states']} ({gi['pct_medium_protection']:.0f}%)")
        report_lines.append(f"   High: {gi['high_protection_states']} ({gi['pct_high_protection']:.0f}%)")
        report_lines.append(f"   GII: {gi['geographic_inequity_index_std']:.2f}")
        
        report_lines.append(f"\n🤝 STATE CONSENSUS:")
        for prov_name, data in sorted(self.stats['state_consensus'].items(), 
                                     key=lambda x: x[1]['percentage'], reverse=True):
            report_lines.append(f"   {prov_name}: {data['percentage']:.0f}% ({data['count']} states)")
        
        fi = self.stats['federal_inaction']
        report_lines.append(f"\n🏛️ FEDERAL INACTION:")
        report_lines.append(f"   State bills: {fi['state_bills_passed']}")
        report_lines.append(f"   Federal bills: {fi['federal_bills_passed']}")
        report_lines.append(f"   Ratio: {fi['state_federal_ratio']:.0f}:1")
        
        eg = self.stats['evidence_gaps']
        report_lines.append(f"\n🔬 EVIDENCE GAPS:")
        report_lines.append(f"   Evidence gap: {eg['evidence_gap_percentage']:.1f}%")
        
        report_lines.append("\n\n" + "="*80)
        report_lines.append("METHODOLOGY")
        report_lines.append("="*80)
        
        for section_name, methodology_text in self.methodology.items():
            report_lines.append(f"\n{section_name.upper().replace('_', ' ')}")
            report_lines.append("-"*80)
            report_lines.append(methodology_text)
        
        report_text = '\n'.join(report_lines)
        with open(f"{self.output_dir}/COMPREHENSIVE_MEMO_STATISTICS.txt", 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        # CSV summary
        stats_flat = [
            {'Category': 'Dataset', 'Metric': 'Total Bills', 'Value': self.stats['total_bills']},
            {'Category': 'Dataset', 'Metric': 'Children-Related Passed', 'Value': self.stats['total_children_passed_bills']},
            {'Category': 'Geographic', 'Metric': 'Low %', 'Value': f"{gi['pct_low_protection']:.1f}%"},
            {'Category': 'Geographic', 'Metric': 'High %', 'Value': f"{gi['pct_high_protection']:.1f}%"},
            {'Category': 'Geographic', 'Metric': 'GII', 'Value': f"{gi['geographic_inequity_index_std']:.2f}"},
            {'Category': 'Federal', 'Metric': 'Ratio', 'Value': f"{fi['state_federal_ratio']:.0f}:1"},
            {'Category': 'Evidence', 'Metric': 'Gap %', 'Value': f"{eg['evidence_gap_percentage']:.1f}%"}
        ]
        
        stats_summary_df = pd.DataFrame(stats_flat)
        stats_summary_df.to_csv(f"{self.output_dir}/KEY_STATISTICS_SUMMARY.csv", index=False)
        
        print(f"  ✓ Report: COMPREHENSIVE_MEMO_STATISTICS.txt")
        print(f"  ✓ Summary: KEY_STATISTICS_SUMMARY.csv")

def main():
    """Main execution"""
    state_file = "Technology Policy Tracking - Updated - US State.csv"
    federal_file = "Technology Policy Tracking - Updated - US Federal.csv"
    
    if not os.path.exists(state_file):
        print(f"ERROR: Cannot find {state_file}")
        return
    
    if not os.path.exists(federal_file):
        print(f"ERROR: Cannot find {federal_file}")
        return
    
    analyzer = PolicyMemoDataVerification(state_file, federal_file)
    analyzer.compute_all_statistics()
    
    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)
    print("\nOutput Files:")
    print("  1. COMPREHENSIVE_MEMO_STATISTICS.txt")
    print("  2. KEY_STATISTICS_SUMMARY.csv")
    print("  3. state_protection_scores.csv")
    print("  4. state_consensus_provisions.csv")
    print("  5. visualizations/*.png")

if __name__ == "__main__":
    main()
