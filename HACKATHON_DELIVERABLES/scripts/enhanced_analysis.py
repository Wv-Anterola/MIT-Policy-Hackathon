"""
Enhanced Analysis for MIT Hackathon Challenge
Generates additional data-driven insights for federal policy recommendations
Focuses on: geographic inequity, compliance complexity, consensus patterns, and evidence gaps
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from collections import Counter, defaultdict
import re

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

class EnhancedPolicyAnalyzer:
    def __init__(self, state_file, federal_file=None):
        """Initialize with data files"""
        self.state_df = pd.read_csv(state_file, encoding='utf-8', low_memory=False)
        if federal_file:
            self.federal_df = pd.read_csv(federal_file, encoding='utf-8', low_memory=False)
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"enhanced_results/analysis_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"Output directory: {self.output_dir}\n")
    
    def analyze_geographic_inequity(self):
        """Analyze differences in protections across states"""
        print("="*80)
        print("GEOGRAPHIC INEQUITY ANALYSIS")
        print("="*80)
        
        # Filter for children-related passed bills
        children_keywords = ['child', 'minor', 'youth', 'student', 'teen', 'kid', 'adolescent']
        mask = self.state_df['Status'].str.contains('Passed', na=False)
        for keyword in children_keywords:
            mask |= (
                self.state_df['Name'].str.contains(keyword, case=False, na=False) |
                self.state_df['Description'].str.contains(keyword, case=False, na=False)
            )
        
        children_passed = self.state_df[mask & self.state_df['Status'].str.contains('Passed', na=False)]
        
        # Calculate protection scores by state
        protection_scores = {}
        provisions = {
            'age_verification': ['age verif', 'age assurance', 'age check'],
            'data_privacy': ['data privacy', 'data protection', 'personal data', 'minimal collection'],
            'parental_control': ['parental consent', 'parental control', 'parent access'],
            'platform_liability': ['liability', 'duty of care', 'negligent harm'],
            'content_safety': ['content moderation', 'harmful content', 'filter'],
            'mental_health': ['mental health', 'addiction', 'wellness', 'time limit'],
            'transparency': ['transparency', 'disclosure', 'report'],
            'education': ['education', 'training', 'awareness', 'literacy']
        }
        
        for state in children_passed['State'].unique():
            state_bills = children_passed[children_passed['State'] == state]
            score = 0
            provisions_present = []
            
            for prov_name, keywords in provisions.items():
                for keyword in keywords:
                    if any(state_bills['Description'].str.contains(keyword, case=False, na=False)):
                        score += 1
                        provisions_present.append(prov_name)
                        break
            
            protection_scores[state] = {
                'score': score,
                'bills': len(state_bills),
                'provisions': list(set(provisions_present))
            }
        
        # Create protection tier visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Sort states by protection score
        sorted_states = sorted(protection_scores.items(), key=lambda x: x[1]['score'], reverse=True)
        states = [s[0] for s in sorted_states[:20]]
        scores = [s[1]['score'] for s in sorted_states[:20]]
        
        # Color code by tier
        colors = []
        for score in scores:
            if score >= 6:
                colors.append('#27ae60')  # High protection (green)
            elif score >= 4:
                colors.append('#f39c12')  # Medium protection (orange)
            else:
                colors.append('#e74c3c')  # Low protection (red)
        
        bars = ax1.barh(states, scores, color=colors, edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Protection Score (0-8)', fontweight='bold', fontsize=12)
        ax1.set_title('State-by-State Youth Protection Scores\n(Geographic Inequity)', 
                     fontweight='bold', fontsize=14)
        ax1.grid(axis='x', alpha=0.3)
        
        # Add tier labels
        ax1.axvline(x=6, color='green', linestyle='--', alpha=0.5, label='High Protection (6+)')
        ax1.axvline(x=4, color='orange', linestyle='--', alpha=0.5, label='Medium Protection (4-5)')
        ax1.legend(fontsize=9)
        
        for i, (state, score) in enumerate(zip(states, scores)):
            ax1.text(score + 0.1, i, str(score), va='center', fontweight='bold')
        
        # Distribution of protection levels
        all_scores = [s[1]['score'] for s in sorted_states]
        tiers = {'High (6-8)': sum(1 for s in all_scores if s >= 6),
                'Medium (4-5)': sum(1 for s in all_scores if 4 <= s < 6),
                'Low (0-3)': sum(1 for s in all_scores if s < 4)}
        
        wedges, texts, autotexts = ax2.pie(tiers.values(), labels=tiers.keys(), autopct='%1.1f%%',
                                           colors=['#27ae60', '#f39c12', '#e74c3c'],
                                           startangle=90, textprops={'fontweight': 'bold'})
        ax2.set_title('Distribution of State Protection Levels\n(Equity Gap Analysis)', 
                     fontweight='bold', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/geographic_inequity_analysis.png")
        plt.close()
        
        # Save detailed scores
        inequity_df = pd.DataFrame([
            {
                'State': state,
                'Protection_Score': data['score'],
                'Bills_Passed': data['bills'],
                'Provisions_Count': len(data['provisions']),
                'Provisions': ', '.join(data['provisions']),
                'Tier': 'High' if data['score'] >= 6 else 'Medium' if data['score'] >= 4 else 'Low'
            }
            for state, data in sorted_states
        ])
        inequity_df.to_csv(f"{self.output_dir}/geographic_inequity_scores.csv", index=False)
        
        print(f"\n📊 Protection Score Analysis:")
        print(f"   High Protection States (6-8): {tiers['High (6-8)']} states")
        print(f"   Medium Protection States (4-5): {tiers['Medium (4-5)']} states")
        print(f"   Low Protection States (0-3): {tiers['Low (0-3)']} states")
        print(f"   Geographic Inequity Index: {np.std(all_scores):.2f} (higher = more unequal)")
        
        return inequity_df
    
    def analyze_compliance_complexity(self):
        """Analyze regulatory burden and variation across states"""
        print("\n" + "="*80)
        print("COMPLIANCE COMPLEXITY ANALYSIS")
        print("="*80)
        
        passed_bills = self.state_df[self.state_df['Status'].str.contains('Passed', na=False)]
        
        # Extract unique requirements across states
        requirements = {
            'Age Verification Required': ['age verif', 'verify age', 'age check', 'age assurance'],
            'Parental Consent Required': ['parental consent', 'parent approval', 'guardian consent'],
            'Data Privacy Standards': ['data privacy', 'data protection', 'privacy by design'],
            'Platform Liability': ['liability', 'civil action', 'damages', 'penalty'],
            'Transparency Reports': ['transparency report', 'annual report', 'disclosure'],
            'Content Moderation': ['content moderation', 'content filter', 'harmful content'],
            'Design Standards': ['design standard', 'default setting', 'design feature'],
            'Enforcement Mechanisms': ['attorney general', 'consumer protection', 'enforcement']
        }
        
        # Track which states have which requirements
        state_requirements = defaultdict(list)
        for state in passed_bills['State'].unique():
            state_bills = passed_bills[passed_bills['State'] == state]
            for req_name, keywords in requirements.items():
                for keyword in keywords:
                    if any(state_bills['Description'].str.contains(keyword, case=False, na=False)):
                        state_requirements[state].append(req_name)
                        break
        
        # Create compliance complexity matrix
        req_matrix = []
        states_list = list(state_requirements.keys())
        for state in states_list:
            row = [1 if req in state_requirements[state] else 0 for req in requirements.keys()]
            req_matrix.append(row)
        
        req_df = pd.DataFrame(req_matrix, columns=requirements.keys(), index=states_list)
        
        # Visualize compliance complexity
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 14))
        
        # Heatmap of requirements by state
        sns.heatmap(req_df.T, cmap='RdYlGn', cbar_kws={'label': 'Requirement Present'},
                   ax=ax1, linewidths=0.5, linecolor='gray')
        ax1.set_title('State Regulatory Requirement Matrix\n(Compliance Complexity for Platforms)',
                     fontweight='bold', fontsize=14)
        ax1.set_xlabel('States', fontweight='bold')
        ax1.set_ylabel('Requirements', fontweight='bold')
        
        # Requirement frequency across states
        req_counts = req_df.sum(axis=0).sort_values(ascending=True)
        colors_req = plt.cm.viridis(np.linspace(0.3, 0.9, len(req_counts)))
        bars = ax2.barh(req_counts.index, req_counts.values, color=colors_req, 
                       edgecolor='black', alpha=0.8)
        ax2.set_xlabel('Number of States with Requirement', fontweight='bold', fontsize=12)
        ax2.set_title('Prevalence of Different Regulatory Requirements\n(Standardization Opportunity)',
                     fontweight='bold', fontsize=14)
        ax2.grid(axis='x', alpha=0.3)
        
        for i, (req, count) in enumerate(req_counts.items()):
            percentage = (count / len(states_list)) * 100
            ax2.text(count + 0.5, i, f'{count} ({percentage:.1f}%)', 
                    va='center', fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/compliance_complexity_matrix.png")
        plt.close()
        
        # Calculate complexity metrics
        total_states = len(states_list)
        avg_requirements = req_df.sum(axis=1).mean()
        variation = req_df.sum(axis=1).std()
        
        print(f"\n📊 Compliance Complexity Metrics:")
        print(f"   States with passed legislation: {total_states}")
        print(f"   Average requirements per state: {avg_requirements:.2f}")
        print(f"   Variation in requirements: {variation:.2f}")
        print(f"   Most common requirement: {req_counts.idxmax()} ({req_counts.max()} states)")
        print(f"   Least common requirement: {req_counts.idxmin()} ({req_counts.min()} states)")
        
        # Save detailed compliance data
        compliance_df = pd.DataFrame([
            {
                'State': state,
                'Total_Requirements': len(reqs),
                'Requirements': ', '.join(reqs),
                'Compliance_Burden': 'High' if len(reqs) >= 6 else 'Medium' if len(reqs) >= 4 else 'Low'
            }
            for state, reqs in state_requirements.items()
        ])
        compliance_df = compliance_df.sort_values('Total_Requirements', ascending=False)
        compliance_df.to_csv(f"{self.output_dir}/compliance_complexity_by_state.csv", index=False)
        
        return compliance_df
    
    def analyze_temporal_momentum(self):
        """Analyze legislative momentum and timing patterns"""
        print("\n" + "="*80)
        print("LEGISLATIVE MOMENTUM ANALYSIS")
        print("="*80)
        
        # Extract years from dates
        self.state_df['Year'] = pd.to_datetime(self.state_df['status_date'], errors='coerce').dt.year
        
        # Filter for children-related bills
        children_keywords = ['child', 'minor', 'youth', 'student', 'teen', 'kid', 'adolescent',
                            'social media', 'online safety', 'data privacy', 'age verification']
        mask = pd.Series([False] * len(self.state_df))
        for keyword in children_keywords:
            mask |= (
                self.state_df['Name'].str.contains(keyword, case=False, na=False) |
                self.state_df['Description'].str.contains(keyword, case=False, na=False)
            )
        
        children_bills = self.state_df[mask]
        
        # Analyze by year and status
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
        
        # 1. Bills introduced over time
        yearly_counts = children_bills.groupby(['Year', 'Status']).size().unstack(fill_value=0)
        yearly_counts = yearly_counts[yearly_counts.index.notna()]
        
        if 'Passed' in yearly_counts.columns:
            yearly_counts[['Introduced', 'Passed']].plot(kind='bar', ax=ax1, 
                                                          color=['#3498db', '#27ae60'],
                                                          edgecolor='black', alpha=0.8)
        else:
            yearly_counts['Introduced'].plot(kind='bar', ax=ax1, color='#3498db',
                                            edgecolor='black', alpha=0.8)
        
        ax1.set_xlabel('Year', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax1.set_title('Youth Online Safety Legislative Activity by Year\n(Momentum Analysis)',
                     fontweight='bold', fontsize=14)
        ax1.legend(fontsize=10)
        ax1.grid(axis='y', alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Pass rate over time
        if 'Passed' in yearly_counts.columns and 'Introduced' in yearly_counts.columns:
            pass_rates = (yearly_counts['Passed'] / yearly_counts['Introduced'] * 100).dropna()
            ax2.plot(pass_rates.index, pass_rates.values, marker='o', linewidth=3,
                    color='#e74c3c', markersize=10)
            ax2.fill_between(pass_rates.index, pass_rates.values, alpha=0.3, color='#e74c3c')
            ax2.set_xlabel('Year', fontweight='bold', fontsize=12)
            ax2.set_ylabel('Pass Rate (%)', fontweight='bold', fontsize=12)
            ax2.set_title('Legislative Success Rate Over Time\n(Effectiveness Trend)',
                         fontweight='bold', fontsize=14)
            ax2.grid(True, alpha=0.3)
            
            for x, y in zip(pass_rates.index, pass_rates.values):
                ax2.text(x, y + 1, f'{y:.1f}%', ha='center', fontweight='bold', fontsize=9)
        
        # 3. Top active states by year
        recent_years = children_bills[children_bills['Year'] >= 2023]
        top_states = recent_years['State'].value_counts().head(10)
        colors_states = plt.cm.plasma(np.linspace(0.2, 0.9, len(top_states)))
        bars = ax3.barh(top_states.index, top_states.values, color=colors_states,
                       edgecolor='black', alpha=0.8)
        ax3.set_xlabel('Number of Bills (2023-2025)', fontweight='bold', fontsize=12)
        ax3.set_title('Most Active States in Recent Years\n(Leadership Analysis)',
                     fontweight='bold', fontsize=14)
        ax3.grid(axis='x', alpha=0.3)
        
        for i, (state, count) in enumerate(top_states.items()):
            ax3.text(count + 1, i, str(count), va='center', fontweight='bold')
        
        # 4. Provision evolution
        provision_trends = defaultdict(lambda: defaultdict(int))
        provisions_to_track = {
            'Age Verification': ['age verif', 'age check'],
            'Data Privacy': ['data privacy', 'data protection'],
            'Platform Liability': ['liability', 'duty of care'],
            'Parental Control': ['parental consent', 'parental control']
        }
        
        for _, bill in children_bills.iterrows():
            year = bill['Year']
            if pd.isna(year) or year < 2020:
                continue
            desc = str(bill['Description']).lower()
            for prov_name, keywords in provisions_to_track.items():
                if any(kw in desc for kw in keywords):
                    provision_trends[prov_name][int(year)] += 1
        
        for prov_name, yearly_data in provision_trends.items():
            if yearly_data:
                years = sorted(yearly_data.keys())
                counts = [yearly_data[y] for y in years]
                ax4.plot(years, counts, marker='o', linewidth=2, label=prov_name, markersize=8)
        
        ax4.set_xlabel('Year', fontweight='bold', fontsize=12)
        ax4.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax4.set_title('Evolution of Key Provisions Over Time\n(Policy Trend Analysis)',
                     fontweight='bold', fontsize=14)
        ax4.legend(fontsize=10)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/legislative_momentum_analysis.png")
        plt.close()
        
        print(f"\n📊 Legislative Momentum Insights:")
        if not yearly_counts.empty:
            recent_year = yearly_counts.index[-1]
            print(f"   Most recent year: {int(recent_year)}")
            print(f"   Bills in most recent year: {int(yearly_counts.loc[recent_year].sum())}")
        print(f"   Most active state (2023-2025): {top_states.index[0]} ({top_states.values[0]} bills)")
        
        return children_bills
    
    def analyze_evidence_gaps(self):
        """Identify areas where more data is needed"""
        print("\n" + "="*80)
        print("EVIDENCE GAPS & DATA NEEDS ANALYSIS")
        print("="*80)
        
        passed_bills = self.state_df[self.state_df['Status'].str.contains('Passed', na=False)]
        
        # Key areas where data is often missing or insufficient
        evidence_areas = {
            'Compliance Costs': {
                'mentioned': ['compliance cost', 'implementation cost', 'fiscal impact'],
                'quantified': ['dollar', '$', 'million', 'thousand', 'budget']
            },
            'Effectiveness Metrics': {
                'mentioned': ['effectiveness', 'impact', 'outcome', 'result'],
                'quantified': ['percentage', '%', 'reduction', 'increase', 'measure']
            },
            'Platform Impact': {
                'mentioned': ['platform impact', 'social media', 'effect on'],
                'quantified': ['user data', 'engagement', 'usage', 'metric']
            },
            'Mental Health Evidence': {
                'mentioned': ['mental health', 'wellbeing', 'addiction', 'harm'],
                'quantified': ['study', 'research', 'data', 'evidence']
            },
            'Privacy Protections': {
                'mentioned': ['privacy', 'data protection', 'personal data'],
                'quantified': ['encryption', 'anonymization', 'deletion', 'minimization']
            }
        }
        
        gap_analysis = {}
        for area, keywords in evidence_areas.items():
            mentioned = 0
            quantified = 0
            
            for _, bill in passed_bills.iterrows():
                desc = str(bill['Description']).lower()
                
                # Check if area is mentioned
                if any(kw in desc for kw in keywords['mentioned']):
                    mentioned += 1
                    
                    # Check if quantitative data is provided
                    if any(kw in desc for kw in keywords['quantified']):
                        quantified += 1
            
            gap_analysis[area] = {
                'mentioned': mentioned,
                'quantified': quantified,
                'gap_percentage': ((mentioned - quantified) / mentioned * 100) if mentioned > 0 else 100
            }
        
        # Visualize evidence gaps
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        
        # Gap visualization
        areas = list(gap_analysis.keys())
        mentioned = [gap_analysis[a]['mentioned'] for a in areas]
        quantified = [gap_analysis[a]['quantified'] for a in areas]
        gaps = [gap_analysis[a]['gap_percentage'] for a in areas]
        
        x = np.arange(len(areas))
        width = 0.35
        
        bars1 = ax1.bar(x - width/2, mentioned, width, label='Mentioned', 
                       color='#3498db', edgecolor='black', alpha=0.8)
        bars2 = ax1.bar(x + width/2, quantified, width, label='Quantified with Data',
                       color='#27ae60', edgecolor='black', alpha=0.8)
        
        ax1.set_xlabel('Evidence Area', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax1.set_title('Evidence Quality in Passed Legislation\n(Data Availability Analysis)',
                     fontweight='bold', fontsize=14)
        ax1.set_xticks(x)
        ax1.set_xticklabels(areas, rotation=45, ha='right')
        ax1.legend(fontsize=11)
        ax1.grid(axis='y', alpha=0.3)
        
        # Gap percentage
        colors_gap = ['#e74c3c' if g > 70 else '#f39c12' if g > 40 else '#27ae60' for g in gaps]
        bars = ax2.barh(areas, gaps, color=colors_gap, edgecolor='black', alpha=0.8)
        ax2.set_xlabel('Evidence Gap (%)', fontweight='bold', fontsize=12)
        ax2.set_title('Evidence Gap Severity\n(Higher = More Data Needed)',
                     fontweight='bold', fontsize=14)
        ax2.grid(axis='x', alpha=0.3)
        ax2.axvline(x=70, color='red', linestyle='--', alpha=0.5, label='Critical Gap (>70%)')
        ax2.axvline(x=40, color='orange', linestyle='--', alpha=0.5, label='Moderate Gap (40-70%)')
        ax2.legend(fontsize=9)
        
        for i, (area, gap) in enumerate(zip(areas, gaps)):
            ax2.text(gap + 1, i, f'{gap:.1f}%', va='center', fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/evidence_gaps_analysis.png")
        plt.close()
        
        # Save gap analysis
        gap_df = pd.DataFrame([
            {
                'Evidence_Area': area,
                'Bills_Mentioning': data['mentioned'],
                'Bills_With_Data': data['quantified'],
                'Evidence_Gap_Pct': data['gap_percentage'],
                'Priority': 'Critical' if data['gap_percentage'] > 70 else 'Moderate' if data['gap_percentage'] > 40 else 'Adequate'
            }
            for area, data in gap_analysis.items()
        ])
        gap_df = gap_df.sort_values('Evidence_Gap_Pct', ascending=False)
        gap_df.to_csv(f"{self.output_dir}/evidence_gaps_priority.csv", index=False)
        
        print(f"\n📊 Evidence Gap Analysis:")
        for area, data in gap_analysis.items():
            print(f"   {area}:")
            print(f"      Mentioned: {data['mentioned']} bills")
            print(f"      With quantitative data: {data['quantified']} bills")
            print(f"      Evidence gap: {data['gap_percentage']:.1f}%")
        
        return gap_df
    
    def generate_federal_framework_recommendations(self, inequity_df, compliance_df):
        """Generate comprehensive federal framework recommendations"""
        print("\n" + "="*80)
        print("FEDERAL FRAMEWORK RECOMMENDATIONS")
        print("="*80)
        
        recommendations = {
            'uniform_standards': [],
            'state_flexibility': [],
            'preemption_policy': [],
            'implementation': []
        }
        
        # Analyze which provisions should be uniform
        high_adoption_provisions = compliance_df[compliance_df['Total_Requirements'] >= 5]
        
        recommendations['uniform_standards'] = [
            "**Uniform Federal Standards** (High Consensus Areas):",
            "- Age Verification Requirements: Standardize methods and privacy protections",
            "- Data Privacy Baseline: Minimum protections for minors' personal data",
            "- Platform Duty of Care: Clear liability framework for negligent harm",
            "- Transparency Requirements: Standardized reporting on safety measures",
            "",
            "**Rationale**: These provisions appear in majority of state laws, indicating broad consensus."
        ]
        
        recommendations['state_flexibility'] = [
            "**State Flexibility Areas** (Local Context Matters):",
            "- Content Moderation Standards: Reflect local community values",
            "- Educational Requirements: Align with state curricula",
            "- Enforcement Mechanisms: Leverage existing state agencies",
            "- Implementation Timelines: Consider state resource availability",
            "",
            "**Rationale**: Geographic and cultural variation requires local adaptation."
        ]
        
        recommendations['preemption_policy'] = [
            "**Preemption Framework** (Floor, Not Ceiling):",
            "- Federal law establishes minimum protections (floor)",
            "- States may exceed federal standards (ceiling) in specific areas",
            "- Uniform standards for interstate platforms (prevent fragmentation)",
            "- State autonomy for local education and enforcement",
            "",
            "**Rationale**: Balance national consistency with state innovation."
        ]
        
        recommendations['implementation'] = [
            "**Implementation Strategy**:",
            "- Phase 1 (Year 1): Large platforms (>10M users)",
            "- Phase 2 (Year 2): Medium platforms (1-10M users)",
            "- Phase 3 (Year 3): Small platforms (<1M users)",
            "- Graduated compliance support for smaller entities",
            "- Federal-state coordination mechanism",
            "",
            "**Support Mechanisms**:",
            "- Technical assistance from FTC/NTIA",
            "- Safe harbor for good-faith compliance",
            "- Regular review and adaptation process",
            "- Multi-stakeholder advisory council"
        ]
        
        # Save recommendations
        with open(f"{self.output_dir}/FEDERAL_FRAMEWORK_RECOMMENDATIONS.md", 'w', encoding='utf-8') as f:
            f.write("# Federal Framework Recommendations for Youth Online Safety\n\n")
            f.write("*Data-Driven Policy Recommendations from State Legislative Analysis*\n\n")
            f.write("---\n\n")
            
            for section, content in recommendations.items():
                f.write("## " + section.replace('_', ' ').title() + "\n\n")
                for line in content:
                    f.write(line + "\n")
                f.write("\n")
            
            # Add key metrics
            f.write("---\n\n")
            f.write("## Supporting Data\n\n")
            f.write(f"- **States with legislation**: {len(inequity_df)} states\n")
            f.write(f"- **Geographic inequity index**: {inequity_df['Protection_Score'].std():.2f}\n")
            f.write(f"- **Average state requirements**: {compliance_df['Total_Requirements'].mean():.2f}\n")
            f.write(f"- **Compliance complexity variation**: {compliance_df['Total_Requirements'].std():.2f}\n")
            f.write("\n")
            f.write("### High-Protection States (Models for Federal Standards)\n")
            for _, row in inequity_df[inequity_df['Tier'] == 'High'].head(5).iterrows():
                f.write(f"- **{row['State']}**: {row['Protection_Score']} provisions, {row['Bills_Passed']} bills\n")
        
        print("\n✅ Federal framework recommendations saved")
        print(f"📄 File: {self.output_dir}/FEDERAL_FRAMEWORK_RECOMMENDATIONS.md")
        
    def run_full_analysis(self):
        """Run all analyses"""
        print("="*80)
        print("ENHANCED ANALYSIS FOR MIT HACKATHON")
        print("Youth Online Safety Federal Framework Development")
        print("="*80)
        print()
        
        # Run all analyses
        inequity_df = self.analyze_geographic_inequity()
        compliance_df = self.analyze_compliance_complexity()
        momentum_df = self.analyze_temporal_momentum()
        gaps_df = self.analyze_evidence_gaps()
        
        # Generate recommendations
        self.generate_federal_framework_recommendations(inequity_df, compliance_df)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n📁 All results saved to: {self.output_dir}")
        print("\n📊 Generated Files:")
        print("   Visualizations:")
        print("   - geographic_inequity_analysis.png")
        print("   - compliance_complexity_matrix.png")
        print("   - legislative_momentum_analysis.png")
        print("   - evidence_gaps_analysis.png")
        print("\n   Data Tables:")
        print("   - geographic_inequity_scores.csv")
        print("   - compliance_complexity_by_state.csv")
        print("   - evidence_gaps_priority.csv")
        print("\n   Policy Documents:")
        print("   - FEDERAL_FRAMEWORK_RECOMMENDATIONS.md")
        print("\n✅ Enhanced analysis complete!")


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EnhancedPolicyAnalyzer(
        state_file="Technology Policy Tracking - Updated - US State.csv",
        federal_file="Technology Policy Tracking - Updated - US Federal.csv"
    )
    
    # Run full analysis
    analyzer.run_full_analysis()
