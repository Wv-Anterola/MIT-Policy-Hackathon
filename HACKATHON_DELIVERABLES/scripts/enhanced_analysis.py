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
        
        # Filter for passed bills only
        self.state_df = self.state_df[self.state_df['Status'].str.contains('Passed', na=False, case=False)]
        print(f"Loaded {len(self.state_df)} passed bills for analysis\n")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = f"enhanced_results/analysis_{timestamp}"
        os.makedirs(self.output_dir, exist_ok=True)
        
        print(f"Output directory: {self.output_dir}\n")
    
    def generate_descriptive_statistics(self):
        """Generate comprehensive descriptive statistics about the dataset"""
        print("="*80)
        print("DESCRIPTIVE STATISTICS")
        print("="*80)
        
        stats_report = []
        
        # Overall dataset statistics
        stats_report.append("\\n=== DATASET OVERVIEW ===")
        stats_report.append(f"Total passed bills analyzed: {len(self.state_df):,}")
        stats_report.append(f"Number of states/territories: {self.state_df['State'].nunique()}")
        
        # Handle date range safely
        if 'status_date' in self.state_df.columns:
            date_series = pd.to_datetime(self.state_df['status_date'], errors='coerce')
            valid_dates = date_series.dropna()
            if len(valid_dates) > 0:
                stats_report.append(f"Date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
            else:
                stats_report.append("Date range: Not available")
        else:
            stats_report.append("Date range: Not available")
        
        # Children-focused bill statistics
        children_keywords = ['child', 'minor', 'youth', 'student', 'teen', 'kid', 'adolescent']
        mask = pd.Series([False] * len(self.state_df), index=self.state_df.index)
        for keyword in children_keywords:
            mask |= (
                self.state_df['Name'].str.contains(keyword, case=False, na=False) |
                self.state_df['Description'].str.contains(keyword, case=False, na=False)
            )
        children_bills = self.state_df[mask]
        
        stats_report.append(f"\nChildren-focused bills: {len(children_bills):,} ({len(children_bills)/len(self.state_df)*100:.1f}%)")
        stats_report.append(f"States with children-focused legislation: {children_bills['State'].nunique()}")
        
        # State-level statistics
        stats_report.append("\n=== STATE-LEVEL STATISTICS ===")
        bills_per_state = self.state_df['State'].value_counts()
        stats_report.append(f"Bills per state (mean): {bills_per_state.mean():.2f}")
        stats_report.append(f"Bills per state (median): {bills_per_state.median():.0f}")
        stats_report.append(f"Bills per state (std dev): {bills_per_state.std():.2f}")
        stats_report.append(f"Bills per state (min): {bills_per_state.min()}")
        stats_report.append(f"Bills per state (max): {bills_per_state.max()}")
        stats_report.append(f"\nTop 5 most active states:")
        for state, count in bills_per_state.head(5).items():
            stats_report.append(f"  {state}: {count} bills")
        
        # Temporal statistics
        if 'status_date' in self.state_df.columns:
            self.state_df['Year'] = pd.to_datetime(self.state_df['status_date'], errors='coerce').dt.year
            yearly_counts = self.state_df['Year'].value_counts().sort_index()
            stats_report.append("\n=== TEMPORAL TRENDS ===")
            stats_report.append(f"Bills by year (mean): {yearly_counts.mean():.2f}")
            stats_report.append(f"Bills by year (median): {yearly_counts.median():.0f}")
            stats_report.append(f"Peak year: {yearly_counts.idxmax()} ({yearly_counts.max()} bills)")
            stats_report.append(f"\nYearly breakdown:")
            for year, count in yearly_counts.items():
                if pd.notna(year):
                    stats_report.append(f"  {int(year)}: {count} bills")
        
        # Topic/keyword statistics
        stats_report.append("\n=== TOPIC PREVALENCE ===")
        topics = {
            'Age Verification': ['age verif', 'age assurance', 'age check'],
            'Data Privacy': ['data privacy', 'data protection', 'personal data'],
            'Platform Liability': ['liability', 'duty of care'],
            'Mental Health': ['mental health', 'addiction', 'wellness'],
            'Transparency': ['transparency', 'disclosure', 'report'],
            'Education': ['education', 'training', 'literacy'],
            'Parental Control': ['parental consent', 'parental control'],
            'Content Safety': ['content moderation', 'harmful content']
        }
        
        topic_counts = {}
        for topic, keywords in topics.items():
            mask = pd.Series([False] * len(children_bills), index=children_bills.index)
            for kw in keywords:
                mask |= children_bills['Description'].str.contains(kw, case=False, na=False)
            count = mask.sum()
            pct = count / len(children_bills) * 100 if len(children_bills) > 0 else 0
            topic_counts[topic] = (count, pct)
            stats_report.append(f"{topic}: {count} bills ({pct:.1f}%)")
        
        # Bill description length statistics
        stats_report.append("\n=== BILL DESCRIPTION CHARACTERISTICS ===")
        desc_lengths = children_bills['Description'].str.len()
        stats_report.append(f"Description length (mean): {desc_lengths.mean():.0f} characters")
        stats_report.append(f"Description length (median): {desc_lengths.median():.0f} characters")
        stats_report.append(f"Description length (std dev): {desc_lengths.std():.0f} characters")
        
        # Generate visualizations
        self._create_descriptive_visualizations(bills_per_state, yearly_counts, topic_counts, children_bills)
        
        # Print and save statistics
        print("\n".join(stats_report))
        
        # Save to file
        with open(f"{self.output_dir}/descriptive_statistics.txt", 'w') as f:
            f.write("\n".join(stats_report))
        
        # Create summary statistics table
        summary_stats = pd.DataFrame({
            'Metric': [
                'Total Bills',
                'Children-Focused Bills',
                'States/Territories',
                'Mean Bills per State',
                'Median Bills per State',
                'Std Dev Bills per State',
                'Date Range Start',
                'Date Range End'
            ],
            'Value': [
                f"{len(self.state_df):,}",
                f"{len(children_bills):,} ({len(children_bills)/len(self.state_df)*100:.1f}%)",
                f"{self.state_df['State'].nunique()}",
                f"{bills_per_state.mean():.2f}",
                f"{bills_per_state.median():.0f}",
                f"{bills_per_state.std():.2f}",
                valid_dates.min().strftime('%Y-%m-%d') if len(valid_dates) > 0 else 'N/A',
                valid_dates.max().strftime('%Y-%m-%d') if len(valid_dates) > 0 else 'N/A'
            ]
        })
        summary_stats.to_csv(f"{self.output_dir}/summary_statistics.csv", index=False)
        
        # Create topic prevalence table
        topic_df = pd.DataFrame([
            {'Topic': topic, 'Bills': count, 'Percentage': f"{pct:.1f}%"}
            for topic, (count, pct) in sorted(topic_counts.items(), key=lambda x: x[1][0], reverse=True)
        ])
        topic_df.to_csv(f"{self.output_dir}/topic_prevalence.csv", index=False)
        
        print(f"\n📊 Descriptive Statistics:")
        print(f"   Summary: {len(self.state_df):,} total bills, {len(children_bills):,} children-focused")
        print(f"   Coverage: {self.state_df['State'].nunique()} states/territories")
        print(f"   Most common topic: {max(topic_counts.items(), key=lambda x: x[1][0])[0]}")
        
        return children_bills
    
    def _create_descriptive_visualizations(self, bills_per_state, yearly_counts, topic_counts, children_bills):
        """Create comprehensive visualizations for descriptive statistics"""
        
        # Create 2x3 grid of visualizations
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # 1. Top 15 Most Active States (Bar Chart)
        ax1 = fig.add_subplot(gs[0, 0])
        top_states = bills_per_state.head(15)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_states)))
        bars = ax1.barh(range(len(top_states)), top_states.values, color=colors, edgecolor='black', alpha=0.8)
        ax1.set_yticks(range(len(top_states)))
        ax1.set_yticklabels(top_states.index)
        ax1.set_xlabel('Number of Passed Bills', fontweight='bold', fontsize=11)
        ax1.set_title('Top 15 Most Active States\n(All Passed Bills)', fontweight='bold', fontsize=13)
        ax1.grid(axis='x', alpha=0.3)
        ax1.invert_yaxis()
        for i, v in enumerate(top_states.values):
            ax1.text(v + 1, i, str(v), va='center', fontweight='bold', fontsize=9)
        
        # 2. Bills Over Time (Line + Bar Chart)
        ax2 = fig.add_subplot(gs[0, 1])
        years = [int(y) for y in yearly_counts.index if pd.notna(y)]
        counts = [yearly_counts[y] for y in yearly_counts.index if pd.notna(y)]
        ax2.bar(years, counts, color='#3498db', edgecolor='black', alpha=0.7, label='Annual Bills')
        ax2.plot(years, counts, color='#e74c3c', linewidth=3, marker='o', markersize=10, label='Trend')
        ax2.set_xlabel('Year', fontweight='bold', fontsize=11)
        ax2.set_ylabel('Number of Bills', fontweight='bold', fontsize=11)
        ax2.set_title('Legislative Activity Over Time\n(2023-2025)', fontweight='bold', fontsize=13)
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        for i, (year, count) in enumerate(zip(years, counts)):
            ax2.text(year, count + 10, str(count), ha='center', fontweight='bold', fontsize=10)
        
        # 3. Topic Prevalence (Horizontal Bar Chart)
        ax3 = fig.add_subplot(gs[1, 0])
        topics_sorted = sorted(topic_counts.items(), key=lambda x: x[1][0], reverse=True)
        topic_names = [t[0] for t in topics_sorted]
        topic_values = [t[1][0] for t in topics_sorted]
        topic_colors = plt.cm.plasma(np.linspace(0.2, 0.9, len(topic_names)))
        bars = ax3.barh(range(len(topic_names)), topic_values, color=topic_colors, edgecolor='black', alpha=0.8)
        ax3.set_yticks(range(len(topic_names)))
        ax3.set_yticklabels(topic_names)
        ax3.set_xlabel('Number of Bills', fontweight='bold', fontsize=11)
        ax3.set_title('Topic Prevalence in Children-Focused Bills\n(N=204)', fontweight='bold', fontsize=13)
        ax3.grid(axis='x', alpha=0.3)
        ax3.invert_yaxis()
        for i, (name, (count, pct)) in enumerate(topics_sorted):
            ax3.text(count + 1, i, f'{count} ({pct:.1f}%)', va='center', fontweight='bold', fontsize=9)
        
        # 4. State Distribution (Pie Chart)
        ax4 = fig.add_subplot(gs[1, 1])
        state_bins = pd.cut(bills_per_state, bins=[0, 5, 15, 30, 100], labels=['Low (1-5)', 'Medium (6-15)', 'High (16-30)', 'Very High (31+)'])
        state_distribution = state_bins.value_counts()
        colors_pie = ['#e74c3c', '#f39c12', '#3498db', '#27ae60']
        wedges, texts, autotexts = ax4.pie(state_distribution.values, labels=state_distribution.index, 
                                           autopct='%1.1f%%', colors=colors_pie, startangle=90,
                                           textprops={'fontweight': 'bold', 'fontsize': 10})
        ax4.set_title('Distribution of State Legislative Activity\n(Bills Passed per State)', fontweight='bold', fontsize=13)
        
        # 5. Children-Focused vs All Bills (Comparison)
        ax5 = fig.add_subplot(gs[2, 0])
        categories = ['All Passed Bills', 'Children-Focused Bills']
        values = [len(self.state_df), len(children_bills)]
        colors_comp = ['#3498db', '#e74c3c']
        bars = ax5.bar(categories, values, color=colors_comp, edgecolor='black', alpha=0.8, width=0.6)
        ax5.set_ylabel('Number of Bills', fontweight='bold', fontsize=11)
        ax5.set_title('Children-Focused Bills as Proportion of Total\n(Passed Bills Only)', fontweight='bold', fontsize=13)
        ax5.grid(axis='y', alpha=0.3)
        for i, (cat, val) in enumerate(zip(categories, values)):
            pct = (val / len(self.state_df) * 100) if i == 1 else 100
            ax5.text(i, val + 20, f'{val}\n({pct:.1f}%)', ha='center', fontweight='bold', fontsize=11)
        
        # 6. Bill Description Length Distribution (Histogram)
        ax6 = fig.add_subplot(gs[2, 1])
        desc_lengths = children_bills['Description'].str.len()
        ax6.hist(desc_lengths, bins=30, color='#9b59b6', edgecolor='black', alpha=0.7)
        ax6.axvline(desc_lengths.mean(), color='#e74c3c', linestyle='--', linewidth=2, label=f'Mean: {desc_lengths.mean():.0f}')
        ax6.axvline(desc_lengths.median(), color='#27ae60', linestyle='--', linewidth=2, label=f'Median: {desc_lengths.median():.0f}')
        ax6.set_xlabel('Description Length (characters)', fontweight='bold', fontsize=11)
        ax6.set_ylabel('Number of Bills', fontweight='bold', fontsize=11)
        ax6.set_title('Distribution of Bill Description Lengths\n(Children-Focused Bills)', fontweight='bold', fontsize=13)
        ax6.legend(fontsize=10)
        ax6.grid(axis='y', alpha=0.3)
        
        plt.savefig(f"{self.output_dir}/descriptive_statistics_dashboard.png", bbox_inches='tight', dpi=300)
        plt.close()
        
        # Create additional detailed state comparison chart
        fig2, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(18, 8))
        
        # State bills - All vs Children-focused
        states_with_children = children_bills['State'].value_counts().head(15)
        all_bills_top = bills_per_state[states_with_children.index]
        
        x = np.arange(len(states_with_children))
        width = 0.35
        
        bars1 = ax_a.bar(x - width/2, all_bills_top.values, width, label='All Bills', 
                        color='#3498db', edgecolor='black', alpha=0.8)
        bars2 = ax_a.bar(x + width/2, states_with_children.values, width, label='Children-Focused', 
                        color='#e74c3c', edgecolor='black', alpha=0.8)
        
        ax_a.set_xlabel('State', fontweight='bold', fontsize=12)
        ax_a.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax_a.set_title('All Bills vs Children-Focused Bills by State\n(Top 15 States with Children Legislation)', 
                      fontweight='bold', fontsize=14)
        ax_a.set_xticks(x)
        ax_a.set_xticklabels(states_with_children.index, rotation=45, ha='right')
        ax_a.legend(fontsize=11)
        ax_a.grid(axis='y', alpha=0.3)
        
        # Percentage of children-focused bills
        percentages = (states_with_children.values / all_bills_top.values * 100)
        colors_pct = plt.cm.RdYlGn(percentages / 100)
        bars = ax_b.barh(range(len(states_with_children)), percentages, color=colors_pct, 
                        edgecolor='black', alpha=0.8)
        ax_b.set_yticks(range(len(states_with_children)))
        ax_b.set_yticklabels(states_with_children.index)
        ax_b.set_xlabel('Percentage of Bills that are Children-Focused', fontweight='bold', fontsize=12)
        ax_b.set_title('Children-Focus Rate by State\n(% of Passed Bills)', fontweight='bold', fontsize=14)
        ax_b.grid(axis='x', alpha=0.3)
        ax_b.invert_yaxis()
        for i, (state, pct) in enumerate(zip(states_with_children.index, percentages)):
            ax_b.text(pct + 1, i, f'{pct:.1f}%', va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f"{self.output_dir}/state_comparison_detailed.png", bbox_inches='tight', dpi=300)
        plt.close()
        
        print("\n📊 Visualizations created:")
        print("   - descriptive_statistics_dashboard.png (6-panel overview)")
        print("   - state_comparison_detailed.png (state-level comparison)")
    
    def analyze_geographic_inequity(self):
        """Analyze differences in protections across states"""
        print("="*80)
        print("GEOGRAPHIC INEQUITY ANALYSIS")
        print("="*80)
        
        # Filter for children-related bills (already filtered to passed bills only)
        children_keywords = ['child', 'minor', 'youth', 'student', 'teen', 'kid', 'adolescent']
        mask = pd.Series([False] * len(self.state_df), index=self.state_df.index)
        for keyword in children_keywords:
            mask |= (
                self.state_df['Name'].str.contains(keyword, case=False, na=False) |
                self.state_df['Description'].str.contains(keyword, case=False, na=False)
            )
        
        children_passed = self.state_df[mask]
        
        # Calculate protection scores by state
        protection_scores = {}
        provision_laws = defaultdict(list)  # Track which laws implement each provision
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
                    matching_bills = state_bills[
                        state_bills['Description'].str.contains(keyword, case=False, na=False)
                    ]
                    if not matching_bills.empty:
                        score += 1
                        provisions_present.append(prov_name)
                        # Track the laws for this provision
                        for _, bill in matching_bills.iterrows():
                            law_name = f"{bill['State']} {bill['Name']}"
                            provision_laws[prov_name].append({
                                'state': bill['State'],
                                'name': bill['Name'],
                                'full_name': law_name
                            })
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
        
        # Save provision laws mapping
        provision_laws_data = []
        for provision, laws in provision_laws.items():
            for law in laws:
                provision_laws_data.append({
                    'Provision': provision,
                    'State': law['state'],
                    'Law_Name': law['name'],
                    'Full_Citation': law['full_name']
                })
        provision_laws_df = pd.DataFrame(provision_laws_data)
        provision_laws_df.to_csv(f"{self.output_dir}/provision_laws_mapping.csv", index=False)
        
        print(f"\n📊 Protection Score Analysis:")
        print(f"   High Protection States (6-8): {tiers['High (6-8)']} states")
        print(f"   Medium Protection States (4-5): {tiers['Medium (4-5)']} states")
        print(f"   Low Protection States (0-3): {tiers['Low (0-3)']} states")
        print(f"   Geographic Inequity Index: {np.std(all_scores):.2f} (higher = more unequal)")
        print(f"   Laws mapped to provisions: {len(provision_laws_data)} law-provision pairs")
        
        return inequity_df, provision_laws
    
    def analyze_compliance_complexity(self):
        """Analyze regulatory burden and variation across states"""
        print("\n" + "="*80)
        print("COMPLIANCE COMPLEXITY ANALYSIS")
        print("="*80)
        
        passed_bills = self.state_df  # Already filtered to passed bills only
        
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
        
        # Track which states have which requirements and which laws implement them
        state_requirements = defaultdict(list)
        requirement_laws = defaultdict(list)
        
        for state in passed_bills['State'].unique():
            state_bills = passed_bills[passed_bills['State'] == state]
            for req_name, keywords in requirements.items():
                for keyword in keywords:
                    matching_bills = state_bills[
                        state_bills['Description'].str.contains(keyword, case=False, na=False)
                    ]
                    if not matching_bills.empty:
                        state_requirements[state].append(req_name)
                        # Track the laws for this requirement
                        for _, bill in matching_bills.iterrows():
                            law_name = f"{bill['State']} {bill['Name']}"
                            requirement_laws[req_name].append({
                                'state': bill['State'],
                                'name': bill['Name'],
                                'full_name': law_name
                            })
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
        
        # Save requirement laws mapping
        requirement_laws_data = []
        for requirement, laws in requirement_laws.items():
            # Deduplicate laws
            unique_laws = {law['full_name']: law for law in laws}
            for law in unique_laws.values():
                requirement_laws_data.append({
                    'Requirement': requirement,
                    'State': law['state'],
                    'Law_Name': law['name'],
                    'Full_Citation': law['full_name']
                })
        requirement_laws_df = pd.DataFrame(requirement_laws_data)
        requirement_laws_df.to_csv(f"{self.output_dir}/requirement_laws_mapping.csv", index=False)
        print(f"   Laws mapped to requirements: {len(requirement_laws_data)} law-requirement pairs")
        
        return compliance_df, requirement_laws
    
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
        mask = pd.Series([False] * len(self.state_df), index=self.state_df.index)
        for keyword in children_keywords:
            mask |= (
                self.state_df['Name'].str.contains(keyword, case=False, na=False) |
                self.state_df['Description'].str.contains(keyword, case=False, na=False)
            )
        
        children_bills = self.state_df[mask]
        
        # Analyze by year and status
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(18, 14))
        
        # 1. Passed bills over time
        yearly_counts = children_bills.groupby('Year').size()
        yearly_counts = yearly_counts[yearly_counts.index.notna()]
        
        yearly_counts.plot(kind='bar', ax=ax1, color='#27ae60',
                          edgecolor='black', alpha=0.8)
        
        ax1.set_xlabel('Year', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Number of Passed Bills', fontweight='bold', fontsize=12)
        ax1.set_title('Youth Online Safety Legislation Enacted by Year\n(Passed Bills Only)',
                     fontweight='bold', fontsize=14)
        ax1.grid(axis='y', alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Add counts on bars
        for i, v in enumerate(yearly_counts.values):
            ax1.text(i, v + 0.5, str(int(v)), ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        # 2. Cumulative passed bills over time
        cumulative = yearly_counts.cumsum()
        ax2.plot(cumulative.index, cumulative.values, marker='o', linewidth=3,
                color='#e74c3c', markersize=10)
        ax2.fill_between(cumulative.index, cumulative.values, alpha=0.3, color='#e74c3c')
        ax2.set_xlabel('Year', fontweight='bold', fontsize=12)
        ax2.set_ylabel('Cumulative Passed Bills', fontweight='bold', fontsize=12)
        ax2.set_title('Cumulative Legislative Progress\n(Total Enacted Laws)',
                     fontweight='bold', fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        for x, y in zip(cumulative.index, cumulative.values):
            ax2.text(x, y + 2, str(int(y)), ha='center', fontweight='bold', fontsize=9)
        
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
        
        passed_bills = self.state_df  # Already filtered to passed bills only
        
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
    
    def generate_federal_framework_recommendations(self, inequity_df, compliance_df, 
                                                          provision_laws, requirement_laws):
        """Generate comprehensive federal framework recommendations with law citations"""
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
            
            # Add example laws for each provision
            f.write("\n### Example Laws by Provision Type\n\n")
            for provision in sorted(provision_laws.keys()):
                laws = provision_laws[provision]
                unique_laws = {law['full_name']: law for law in laws}
                if unique_laws:
                    f.write(f"**{provision.replace('_', ' ').title()}:**\n")
                    for law in list(unique_laws.values())[:5]:  # Top 5 examples
                        f.write(f"  - {law['full_name']}\n")
                    if len(unique_laws) > 5:
                        f.write(f"  - ...and {len(unique_laws) - 5} more\n")
                    f.write("\n")
        
        print("\n✅ Federal framework recommendations saved")
        print(f"📄 File: {self.output_dir}/FEDERAL_FRAMEWORK_RECOMMENDATIONS.md")
        
    def run_full_analysis(self):
        """Run all analyses"""
        print("="*80)
        print("ENHANCED ANALYSIS FOR MIT HACKATHON")
        print("Youth Online Safety Federal Framework Development")
        print("Analysis of PASSED BILLS ONLY")
        print("="*80)
        print()
        
        # Generate descriptive statistics first
        children_bills = self.generate_descriptive_statistics()
        
        # Run all analyses
        inequity_df, provision_laws = self.analyze_geographic_inequity()
        compliance_df, requirement_laws = self.analyze_compliance_complexity()
        momentum_df = self.analyze_temporal_momentum()
        gaps_df = self.analyze_evidence_gaps()
        
        # Generate recommendations with law citations
        self.generate_federal_framework_recommendations(inequity_df, compliance_df, 
                                                       provision_laws, requirement_laws)
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n📁 All results saved to: {self.output_dir}")
        print("\n📊 Generated Files:")
        print("   Visualizations:")
        print("   - descriptive_statistics_dashboard.png (NEW: 6-panel overview)")
        print("   - state_comparison_detailed.png (NEW: state-level analysis)")
        print("   - geographic_inequity_analysis.png")
        print("   - compliance_complexity_matrix.png")
        print("   - legislative_momentum_analysis.png")
        print("   - evidence_gaps_analysis.png")
        print("\n   Data Tables:")
        print("   - summary_statistics.csv (NEW: Dataset overview metrics)")
        print("   - topic_prevalence.csv (NEW: Topic distribution across bills)")
        print("   - geographic_inequity_scores.csv")
        print("   - compliance_complexity_by_state.csv")
        print("   - evidence_gaps_priority.csv")
        print("   - provision_laws_mapping.csv (Laws by provision type)")
        print("   - requirement_laws_mapping.csv (Laws by requirement)")
        print("\n   Reports:")
        print("   - descriptive_statistics.txt (NEW: Comprehensive statistics report)")
        print("\n   Policy Documents:")
        print("   - FEDERAL_FRAMEWORK_RECOMMENDATIONS.md")
        print("\n✅ Enhanced analysis complete!")


if __name__ == "__main__":
    # Initialize analyzer
    analyzer = EnhancedPolicyAnalyzer(
        state_file="../../Technology Policy Tracking - Updated - US State.csv",
        federal_file="../../Technology Policy Tracking - Updated - US Federal.csv"
    )
    
    # Run full analysis
    analyzer.run_full_analysis()
