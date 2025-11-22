"""
Challenge-Focused Analysis for Youth Online Safety Standards

Addresses the MIT Hackathon Challenge Questions:
1. How can state legislation provide insight into holistic solutions?
2. Where do states agree or disagree?
3. What should be kept at state level?
4. What approaches ensure strong privacy + long-term effectiveness?

Data-driven analysis from Tech Policy Tracker
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import os
import re
from datetime import datetime

class ChallengeAnalyzer:
    """Analyze state legislation to answer federal policy challenge questions"""
    
    def __init__(self, passed_bills_path, all_bills_path=None, output_dir=None):
        """Initialize with paths to analysis data"""
        self.passed_df = pd.read_csv(passed_bills_path)
        self.all_df = pd.read_csv(all_bills_path) if all_bills_path else None
        self.output_dir = output_dir or self._create_output_dir()
        
        # Parse themes column
        self.passed_df['Themes_List'] = self.passed_df['Themes'].apply(
            lambda x: [t.strip() for t in str(x).split(',')] if pd.notna(x) else []
        )
        
        print(f"Loaded {len(self.passed_df)} passed bills from {self.passed_df['State'].nunique()} states")
        print(f"Output directory: {self.output_dir}\n")
    
    def _create_output_dir(self):
        """Create organized output directory"""
        base_dir = "challenge_analysis_results"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_dir, f"analysis_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def _save_plot(self, filename):
        """Save plot to output directory"""
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return filepath
    
    def _save_csv(self, df, filename):
        """Save dataframe to CSV"""
        filepath = os.path.join(self.output_dir, filename)
        df.to_csv(filepath, index=True)
        return filepath
    
    # ===================================================================
    # QUESTION 1: How can state legislation provide holistic insights?
    # ===================================================================
    
    def analyze_holistic_patterns(self):
        """Identify patterns across states that suggest holistic approaches"""
        print("="*80)
        print("Q1: HOLISTIC SOLUTION INSIGHTS FROM STATE LEGISLATION")
        print("="*80)
        
        # 1. Multi-dimensional approach analysis
        print("\n1. MULTI-DIMENSIONAL APPROACHES BY STATE")
        print("-" * 80)
        
        # Define policy dimensions
        dimensions = {
            'Privacy Protection': ['Data Privacy', 'Privacy'],
            'Platform Accountability': ['Liability', 'Platform', 'Social Media'],
            'Content Safety': ['Content Regulation', 'Online Safety'],
            'Parental Rights': ['Parental', 'Consent', 'Control'],
            'Transparency': ['Transparency', 'Disclosure'],
            'Education': ['Education', 'Training', 'Awareness'],
            'Technical Standards': ['Design', 'Testing', 'Standards'],
            'Mental Health': ['Mental Health', 'Wellness']
        }
        
        # Score each state on each dimension
        state_scores = {}
        for state in self.passed_df['State'].unique():
            state_bills = self.passed_df[self.passed_df['State'] == state]
            scores = {}
            
            for dimension, keywords in dimensions.items():
                count = 0
                for _, bill in state_bills.iterrows():
                    text = f"{bill['Name']} {bill['Description']} {bill['Themes']}"
                    if any(kw.lower() in text.lower() for kw in keywords):
                        count += 1
                scores[dimension] = count
            
            state_scores[state] = scores
        
        # Find states with most comprehensive approaches
        state_df = pd.DataFrame(state_scores).T
        state_df['Total_Dimensions'] = (state_df > 0).sum(axis=1)
        state_df['Total_Bills'] = [len(self.passed_df[self.passed_df['State'] == s]) for s in state_df.index]
        
        comprehensive_states = state_df.nlargest(10, 'Total_Dimensions')
        
        print("\nTop 10 Most Comprehensive State Approaches:")
        print(f"{'State':<20} {'Dimensions':<12} {'Bills':<10} {'Key Strengths'}")
        print("-" * 80)
        
        for state, row in comprehensive_states.iterrows():
            dims = row['Total_Dimensions']
            bills = row['Total_Bills']
            strengths = state_df.loc[state].nlargest(3).index.tolist()
            print(f"{state:<20} {dims:<12} {bills:<10} {', '.join(strengths[:2])}")
        
        # 2. Common patterns in comprehensive legislation
        print("\n2. PATTERNS IN COMPREHENSIVE LEGISLATION")
        print("-" * 80)
        
        # States with 5+ dimensions
        comprehensive = state_df[state_df['Total_Dimensions'] >= 5]
        
        print(f"\n{len(comprehensive)} states have comprehensive approaches (5+ dimensions)")
        print("\nCommon combination patterns:")
        
        # Calculate co-occurrence of dimensions
        dimension_pairs = {}
        for state, row in comprehensive.iterrows():
            present_dims = [dim for dim in dimensions.keys() if row[dim] > 0]
            for i, dim1 in enumerate(present_dims):
                for dim2 in present_dims[i+1:]:
                    pair = tuple(sorted([dim1, dim2]))
                    dimension_pairs[pair] = dimension_pairs.get(pair, 0) + 1
        
        sorted_pairs = sorted(dimension_pairs.items(), key=lambda x: x[1], reverse=True)[:5]
        for (dim1, dim2), count in sorted_pairs:
            pct = (count / len(comprehensive)) * 100
            print(f"  • {dim1} + {dim2}: {count} states ({pct:.1f}%)")
        
        # Visualization: Heatmap of state approaches
        plt.figure(figsize=(14, 10))
        
        # Select top 20 states by total bills for visibility
        top_states = state_df.nlargest(20, 'Total_Bills')
        heatmap_data = top_states[list(dimensions.keys())]
        
        sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd', 
                   cbar_kws={'label': 'Number of Bills'})
        plt.title('Multi-Dimensional Approach by State\n(Comprehensive vs Single-Issue Legislation)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Policy Dimension', fontsize=12)
        plt.ylabel('State', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        self._save_plot('holistic_state_heatmap.png')
        
        # Save data
        self._save_csv(state_df, 'holistic_state_scores.csv')
        
        return state_df, dimensions
    
    # ===================================================================
    # QUESTION 2: Where do states agree or disagree?
    # ===================================================================
    
    def analyze_state_consensus(self):
        """Identify areas of agreement and divergence"""
        print("\n" + "="*80)
        print("Q2: STATE CONSENSUS AND DIVERGENCE ANALYSIS")
        print("="*80)
        
        # 1. Provision adoption rates
        print("\n1. UNIVERSAL VS CONTESTED PROVISIONS")
        print("-" * 80)
        
        provisions = {
            'Age Verification': ['age verification', 'age assurance', 'verify age'],
            'Parental Consent': ['parental consent', 'parental permission', 'guardian consent'],
            'Data Privacy': ['data privacy', 'data protection', 'personal information'],
            'Platform Liability': ['liable', 'liability', 'civil action', 'damages'],
            'Content Filtering': ['content filter', 'harmful content', 'content moderation'],
            'Design Standards': ['design standards', 'default settings', 'privacy by design'],
            'Transparency Requirements': ['transparency', 'disclosure', 'reporting requirement'],
            'Time Limits': ['time limit', 'usage limit', 'screen time'],
            'Education Programs': ['education', 'training', 'awareness program'],
            'Algorithmic Regulation': ['algorithm', 'recommendation', 'feed'],
            'Mental Health': ['mental health', 'wellness', 'psychological'],
            'Free Speech Protection': ['free speech', 'first amendment', 'expression']
        }
        
        # Count states adopting each provision
        provision_adoption = {}
        state_provisions = {}
        
        for state in self.passed_df['State'].unique():
            state_bills = self.passed_df[self.passed_df['State'] == state]
            state_text = ' '.join(state_bills['Name'].fillna('') + ' ' + 
                                 state_bills['Description'].fillna('')).lower()
            state_provisions[state] = []
            
            for provision, keywords in provisions.items():
                if any(kw in state_text for kw in keywords):
                    provision_adoption[provision] = provision_adoption.get(provision, 0) + 1
                    state_provisions[state].append(provision)
        
        total_states = len(self.passed_df['State'].unique())
        provision_df = pd.DataFrame([
            {
                'Provision': prov,
                'States': count,
                'Percentage': (count / total_states) * 100,
                'Category': 'Universal' if count >= total_states * 0.75 else
                           'High Consensus' if count >= total_states * 0.5 else
                           'Moderate Adoption' if count >= total_states * 0.25 else
                           'Divergent'
            }
            for prov, count in provision_adoption.items()
        ]).sort_values('Percentage', ascending=False)
        
        print("\nProvision Adoption Rates:")
        print(f"{'Provision':<30} {'States':<10} {'%':<10} {'Consensus Level'}")
        print("-" * 80)
        for _, row in provision_df.iterrows():
            print(f"{row['Provision']:<30} {row['States']:<10} {row['Percentage']:<10.1f} {row['Category']}")
        
        # 2. Regional patterns
        print("\n2. REGIONAL AGREEMENT PATTERNS")
        print("-" * 80)
        
        # Define regions
        regions = {
            'West Coast': ['California', 'Oregon', 'Washington'],
            'Northeast': ['New York', 'Massachusetts', 'Connecticut', 'Vermont', 'New Jersey'],
            'South': ['Texas', 'Florida', 'Georgia', 'Tennessee', 'Louisiana'],
            'Midwest': ['Illinois', 'Michigan', 'Ohio', 'Wisconsin', 'Minnesota']
        }
        
        region_consensus = {}
        for region_name, states in regions.items():
            region_bills = self.passed_df[self.passed_df['State'].isin(states)]
            if len(region_bills) > 0:
                region_text = ' '.join(region_bills['Name'].fillna('') + ' ' + 
                                      region_bills['Description'].fillna('')).lower()
                region_provisions = [p for p, kws in provisions.items() 
                                   if any(kw in region_text for kw in kws)]
                region_consensus[region_name] = region_provisions
        
        print("\nRegional Policy Focus:")
        for region, provs in region_consensus.items():
            print(f"\n{region}:")
            print(f"  Primary Focus: {', '.join(provs[:3])}")
        
        # 3. Visualization: Consensus spectrum
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Bar chart of adoption rates
        colors = provision_df['Category'].map({
            'Universal': '#2ecc71',
            'High Consensus': '#3498db',
            'Moderate Adoption': '#f39c12',
            'Divergent': '#e74c3c'
        })
        
        ax1.barh(provision_df['Provision'], provision_df['Percentage'], color=colors)
        ax1.axvline(x=75, color='green', linestyle='--', alpha=0.5, label='Universal (75%+)')
        ax1.axvline(x=50, color='blue', linestyle='--', alpha=0.5, label='High Consensus (50%+)')
        ax1.axvline(x=25, color='orange', linestyle='--', alpha=0.5, label='Moderate (25%+)')
        ax1.set_xlabel('% of States Adopting', fontsize=12)
        ax1.set_title('State Consensus on Policy Provisions', fontsize=14, fontweight='bold')
        ax1.legend()
        ax1.grid(axis='x', alpha=0.3)
        
        # Provision co-adoption network
        provision_matrix = pd.DataFrame(0, index=provisions.keys(), columns=provisions.keys())
        for state, state_provs in state_provisions.items():
            for p1 in state_provs:
                for p2 in state_provs:
                    if p1 != p2:
                        provision_matrix.loc[p1, p2] += 1
        
        # Show top correlations
        top_6_provisions = provision_df.head(6)['Provision'].tolist()
        matrix_subset = provision_matrix.loc[top_6_provisions, top_6_provisions]
        
        sns.heatmap(matrix_subset, annot=True, fmt='g', cmap='Blues', ax=ax2,
                   cbar_kws={'label': 'States with Both Provisions'})
        ax2.set_title('Provision Co-Adoption Patterns\n(Top 6 Most Common)', 
                     fontsize=14, fontweight='bold')
        ax2.set_xlabel('Provision', fontsize=12)
        ax2.set_ylabel('Provision', fontsize=12)
        
        plt.tight_layout()
        self._save_plot('consensus_analysis.png')
        
        # Save data
        self._save_csv(provision_df, 'provision_consensus.csv')
        
        return provision_df, state_provisions
    
    # ===================================================================
    # QUESTION 3: What should be kept at state level?
    # ===================================================================
    
    def analyze_federalism_balance(self):
        """Determine which areas work better at state vs federal level"""
        print("\n" + "="*80)
        print("Q3: FEDERAL VS STATE JURISDICTION ANALYSIS")
        print("="*80)
        
        print("\n1. CANDIDATES FOR FEDERAL STANDARDIZATION")
        print("-" * 80)
        
        # Criteria for federal standardization:
        # - High interstate consistency (75%+ adoption)
        # - Affects interstate commerce
        # - Technical standards
        # - Fundamental rights
        
        federal_candidates = {
            'Strong Federal Candidates': {
                'criteria': 'Universal adoption + technical/rights focus',
                'provisions': []
            },
            'Federal Framework with State Flexibility': {
                'criteria': 'High consensus but implementation varies',
                'provisions': []
            },
            'Best Left to States': {
                'criteria': 'Low consensus + local context important',
                'provisions': []
            }
        }
        
        # Analyze each provision
        provisions_analysis = []
        
        # Get provision data from previous analysis
        provisions = {
            'Age Verification': ['age verification', 'age assurance'],
            'Data Privacy': ['data privacy', 'data protection'],
            'Platform Liability': ['liability', 'civil action'],
            'Content Standards': ['harmful content', 'content moderation'],
            'Parental Rights': ['parental consent', 'parental control'],
            'Design Requirements': ['design standards', 'default settings'],
            'Transparency': ['transparency', 'disclosure'],
            'Education': ['education', 'training'],
            'Local School Policies': ['school', 'k-12', 'district'],
            'State Agency Oversight': ['attorney general', 'consumer protection']
        }
        
        for provision, keywords in provisions.items():
            state_count = 0
            implementation_varies = False
            
            state_approaches = {}
            for state in self.passed_df['State'].unique():
                state_bills = self.passed_df[self.passed_df['State'] == state]
                state_text = ' '.join(state_bills['Description'].fillna('')).lower()
                
                if any(kw in state_text for kw in keywords):
                    state_count += 1
                    # Extract implementation details
                    state_approaches[state] = state_text
            
            adoption_rate = (state_count / self.passed_df['State'].nunique()) * 100
            
            # Determine categorization
            if adoption_rate >= 75:
                if provision in ['Age Verification', 'Data Privacy', 'Platform Liability']:
                    category = 'Strong Federal Candidates'
                else:
                    category = 'Federal Framework with State Flexibility'
            elif adoption_rate >= 25:
                category = 'Federal Framework with State Flexibility'
            else:
                category = 'Best Left to States'
            
            federal_candidates[category]['provisions'].append({
                'provision': provision,
                'adoption_rate': adoption_rate,
                'states': state_count
            })
            
            provisions_analysis.append({
                'Provision': provision,
                'Adoption_Rate': adoption_rate,
                'States': state_count,
                'Recommendation': category
            })
        
        # Display results
        for category, data in federal_candidates.items():
            print(f"\n{category}:")
            print(f"  Criteria: {data['criteria']}")
            if data['provisions']:
                for item in sorted(data['provisions'], key=lambda x: x['adoption_rate'], reverse=True):
                    print(f"    • {item['provision']}: {item['adoption_rate']:.1f}% ({item['states']} states)")
            else:
                print("    (None identified)")
        
        # 2. State-specific context analysis
        print("\n2. STATE-SPECIFIC CONSIDERATIONS")
        print("-" * 80)
        
        state_specific = {
            'Educational Standards': 'Local control of schools',
            'Enforcement Mechanisms': 'State consumer protection agencies',
            'Implementation Timeline': 'State resource availability',
            'Cultural Values': 'Local community standards',
            'Economic Impact': 'State business environment'
        }
        
        print("\nAreas Requiring State Flexibility:")
        for area, reason in state_specific.items():
            print(f"  • {area}: {reason}")
        
        # 3. Visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Adoption rate distribution
        prov_df = pd.DataFrame(provisions_analysis)
        
        ax1 = axes[0, 0]
        categories = prov_df['Recommendation'].value_counts()
        colors_map = {
            'Strong Federal Candidates': '#27ae60',
            'Federal Framework with State Flexibility': '#3498db',
            'Best Left to States': '#e67e22'
        }
        colors = [colors_map.get(cat, '#95a5a6') for cat in categories.index]
        ax1.pie(categories.values, labels=categories.index, autopct='%1.1f%%',
               colors=colors, startangle=90)
        ax1.set_title('Distribution of Provisions by\nFederal vs State Recommendation',
                     fontsize=12, fontweight='bold')
        
        # Adoption rate spectrum
        ax2 = axes[0, 1]
        prov_sorted = prov_df.sort_values('Adoption_Rate', ascending=True)
        colors = [colors_map[rec] for rec in prov_sorted['Recommendation']]
        ax2.barh(prov_sorted['Provision'], prov_sorted['Adoption_Rate'], color=colors)
        ax2.axvline(x=75, color='green', linestyle='--', alpha=0.5, label='Federal threshold')
        ax2.axvline(x=25, color='orange', linestyle='--', alpha=0.5, label='State threshold')
        ax2.set_xlabel('Adoption Rate (%)', fontsize=11)
        ax2.set_title('Provision Adoption Rates', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(axis='x', alpha=0.3)
        
        # State activity by region
        ax3 = axes[1, 0]
        regions = {
            'West': ['California', 'Oregon', 'Washington', 'Nevada', 'Arizona'],
            'Northeast': ['New York', 'Massachusetts', 'Connecticut', 'Vermont', 'New Jersey', 'Pennsylvania'],
            'South': ['Texas', 'Florida', 'Georgia', 'Tennessee', 'Louisiana', 'Virginia', 'North Carolina'],
            'Midwest': ['Illinois', 'Michigan', 'Ohio', 'Wisconsin', 'Minnesota', 'Indiana', 'Missouri'],
            'Mountain': ['Colorado', 'Utah', 'Montana', 'Idaho', 'Wyoming']
        }
        
        region_counts = {}
        for region, states in regions.items():
            count = len(self.passed_df[self.passed_df['State'].isin(states)])
            region_counts[region] = count
        
        regions_series = pd.Series(region_counts).sort_values(ascending=True)
        ax3.barh(regions_series.index, regions_series.values, color='#3498db')
        ax3.set_xlabel('Number of Passed Bills', fontsize=11)
        ax3.set_title('Regional Variation in Legislative Activity', fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        # Implementation timeline analysis
        ax4 = axes[1, 1]
        if 'Intro Date' in self.passed_df.columns:
            self.passed_df['Year'] = pd.to_datetime(self.passed_df['Intro Date'], 
                                                    format='%d/%m/%Y', errors='coerce').dt.year
            year_counts = self.passed_df['Year'].value_counts().sort_index()
            ax4.plot(year_counts.index, year_counts.values, marker='o', linewidth=2, color='#e74c3c')
            ax4.fill_between(year_counts.index, year_counts.values, alpha=0.3, color='#e74c3c')
            ax4.set_xlabel('Year', fontsize=11)
            ax4.set_ylabel('Bills Passed', fontsize=11)
            ax4.set_title('Legislative Activity Timeline\n(State-led Innovation)', fontsize=12, fontweight='bold')
            ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        self._save_plot('federalism_analysis.png')
        
        # Save data
        self._save_csv(prov_df, 'federalism_recommendations.csv')
        
        return prov_df, federal_candidates
    
    # ===================================================================
    # QUESTION 4: What approaches ensure privacy + effectiveness?
    # ===================================================================
    
    def analyze_privacy_effectiveness(self):
        """Analyze approaches balancing privacy and effectiveness"""
        print("\n" + "="*80)
        print("Q4: PRIVACY + EFFECTIVENESS ANALYSIS")
        print("="*80)
        
        print("\n1. AGE VERIFICATION APPROACHES")
        print("-" * 80)
        
        # Categorize age verification methods
        age_methods = {
            'Government ID': ['government id', 'driver license', 'state id', 'official identification'],
            'Third-Party Verification': ['third party', 'third-party', 'verification service'],
            'Age Estimation': ['age estimation', 'age assurance', 'facial analysis'],
            'Parental Consent': ['parental consent', 'parent approval', 'guardian consent'],
            'Credit Card': ['credit card', 'payment method'],
            'Self-Attestation': ['self-attest', 'declare age', 'affirm age'],
            'Privacy-Preserving': ['privacy preserving', 'privacy-preserving', 'anonymous verification', 'zero knowledge']
        }
        
        method_adoption = {}
        method_states = {}
        
        for method, keywords in age_methods.items():
            states_using = []
            for state in self.passed_df['State'].unique():
                state_bills = self.passed_df[self.passed_df['State'] == state]
                state_text = ' '.join(state_bills['Description'].fillna('')).lower()
                
                if any(kw in state_text for kw in keywords):
                    states_using.append(state)
            
            method_adoption[method] = len(states_using)
            method_states[method] = states_using
        
        method_df = pd.DataFrame([
            {'Method': method, 'States': count, 'Privacy_Score': self._privacy_score(method),
             'Effectiveness_Score': self._effectiveness_score(method)}
            for method, count in method_adoption.items()
        ]).sort_values('States', ascending=False)
        
        print("\nAge Verification Methods:")
        print(f"{'Method':<30} {'States':<10} {'Privacy':<12} {'Effectiveness'}")
        print("-" * 80)
        for _, row in method_df.iterrows():
            privacy_bar = '█' * row['Privacy_Score'] + '░' * (5 - row['Privacy_Score'])
            effect_bar = '█' * row['Effectiveness_Score'] + '░' * (5 - row['Effectiveness_Score'])
            print(f"{row['Method']:<30} {row['States']:<10} {privacy_bar:<12} {effect_bar}")
        
        # 2. Data minimization practices
        print("\n2. DATA MINIMIZATION & RETENTION LIMITS")
        print("-" * 80)
        
        data_practices = {
            'Data Deletion Required': ['delete', 'deletion', 'remove data', 'data retention limit'],
            'Minimal Collection': ['minimal', 'minimum', 'necessary data', 'data minimization'],
            'No Retention of ID': ['not retain', 'no retention', 'cannot retain', 'prohibited from retaining'],
            'Anonymization': ['anonymize', 'anonymous', 'de-identify'],
            'Purpose Limitation': ['purpose limitation', 'specified purpose', 'limited purpose']
        }
        
        practice_counts = {}
        for practice, keywords in data_practices.items():
            count = 0
            for _, bill in self.passed_df.iterrows():
                text = f"{bill['Description']}".lower()
                if any(kw in text for kw in keywords):
                    count += 1
            practice_counts[practice] = count
        
        print("\nData Protection Practices in Legislation:")
        total = len(self.passed_df)
        for practice, count in sorted(practice_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            print(f"  • {practice}: {count} bills ({pct:.1f}%)")
        
        # 3. Long-term effectiveness indicators
        print("\n3. LONG-TERM EFFECTIVENESS MECHANISMS")
        print("-" * 80)
        
        effectiveness_features = {
            'Regular Audits': ['audit', 'periodic review', 'compliance check'],
            'Sunset Provisions': ['sunset', 'expire', 'review date'],
            'Technology Neutral': ['technology neutral', 'adaptable', 'flexible approach'],
            'Industry Standards': ['industry standard', 'best practice', 'technical standard'],
            'Enforcement Mechanisms': ['enforce', 'penalty', 'fine', 'damages'],
            'Reporting Requirements': ['report', 'reporting requirement', 'transparency report']
        }
        
        effectiveness_counts = {}
        for feature, keywords in effectiveness_features.items():
            count = 0
            for _, bill in self.passed_df.iterrows():
                text = f"{bill['Description']}".lower()
                if any(kw in text for kw in keywords):
                    count += 1
            effectiveness_counts[feature] = count
        
        print("\nLong-term Effectiveness Features:")
        for feature, count in sorted(effectiveness_counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            print(f"  • {feature}: {count} bills ({pct:.1f}%)")
        
        # 4. Best practice examples
        print("\n4. BEST PRACTICE EXAMPLES")
        print("-" * 80)
        
        # Find bills with multiple privacy + effectiveness features
        best_practices = []
        for _, bill in self.passed_df.iterrows():
            text = f"{bill['Name']} {bill['Description']}".lower()
            
            privacy_score = sum(1 for practice in data_practices.values() 
                              if any(kw in text for kw in practice))
            effectiveness_score = sum(1 for feature in effectiveness_features.values()
                                     if any(kw in text for kw in feature))
            
            if privacy_score >= 2 and effectiveness_score >= 2:
                best_practices.append({
                    'State': bill['State'],
                    'Bill': bill['Name'],
                    'Privacy_Features': privacy_score,
                    'Effectiveness_Features': effectiveness_score,
                    'Total_Score': privacy_score + effectiveness_score
                })
        
        if best_practices:
            best_df = pd.DataFrame(best_practices).nlargest(10, 'Total_Score')
            print("\nTop 10 Bills with Strong Privacy + Effectiveness:")
            print(f"{'State':<15} {'Privacy':<10} {'Effectiveness':<15} {'Bill Name'}")
            print("-" * 80)
            for _, row in best_df.iterrows():
                bill_name = row['Bill'][:50] + '...' if len(row['Bill']) > 50 else row['Bill']
                print(f"{row['State']:<15} {row['Privacy_Features']:<10} {row['Effectiveness_Features']:<15} {bill_name}")
        
        # 5. Visualization
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # Age verification methods trade-offs
        ax1 = axes[0, 0]
        ax1.scatter(method_df['Privacy_Score'], method_df['Effectiveness_Score'], 
                   s=method_df['States']*50, alpha=0.6, c='#3498db')
        for _, row in method_df.iterrows():
            ax1.annotate(row['Method'], (row['Privacy_Score'], row['Effectiveness_Score']),
                        fontsize=8, alpha=0.7)
        ax1.set_xlabel('Privacy Protection (1-5)', fontsize=11)
        ax1.set_ylabel('Effectiveness (1-5)', fontsize=11)
        ax1.set_title('Age Verification Methods: Privacy vs Effectiveness Trade-offs\n(Bubble size = # of states)',
                     fontsize=12, fontweight='bold')
        ax1.grid(alpha=0.3)
        ax1.set_xlim(0, 6)
        ax1.set_ylim(0, 6)
        
        # Data protection practices
        ax2 = axes[0, 1]
        practices_series = pd.Series(practice_counts).sort_values()
        practices_series.plot(kind='barh', ax=ax2, color='#27ae60')
        ax2.set_xlabel('Number of Bills', fontsize=11)
        ax2.set_title('Data Protection Practices in State Legislation',
                     fontsize=12, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        
        # Effectiveness features
        ax3 = axes[1, 0]
        effectiveness_series = pd.Series(effectiveness_counts).sort_values()
        effectiveness_series.plot(kind='barh', ax=ax3, color='#e74c3c')
        ax3.set_xlabel('Number of Bills', fontsize=11)
        ax3.set_title('Long-term Effectiveness Mechanisms',
                     fontsize=12, fontweight='bold')
        ax3.grid(axis='x', alpha=0.3)
        
        # Privacy-Effectiveness Matrix
        ax4 = axes[1, 1]
        if best_practices:
            best_df = pd.DataFrame(best_practices)
            state_scores = best_df.groupby('State').agg({
                'Privacy_Features': 'mean',
                'Effectiveness_Features': 'mean'
            }).nlargest(15, 'Total_Score')
            
            ax4.scatter(state_scores['Privacy_Features'], state_scores['Effectiveness_Features'],
                       s=200, alpha=0.6, c='#9b59b6')
            for state, row in state_scores.iterrows():
                ax4.annotate(state, (row['Privacy_Features'], row['Effectiveness_Features']),
                           fontsize=9, alpha=0.8)
            ax4.set_xlabel('Average Privacy Features per Bill', fontsize=11)
            ax4.set_ylabel('Average Effectiveness Features per Bill', fontsize=11)
            ax4.set_title('State Performance: Privacy + Effectiveness Balance',
                         fontsize=12, fontweight='bold')
            ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        self._save_plot('privacy_effectiveness_analysis.png')
        
        # Save data
        self._save_csv(method_df, 'age_verification_methods.csv')
        if best_practices:
            self._save_csv(pd.DataFrame(best_practices), 'best_practice_bills.csv')
        
        return method_df, practice_counts, effectiveness_counts
    
    def _privacy_score(self, method):
        """Assign privacy score to age verification method"""
        scores = {
            'Privacy-Preserving': 5,
            'Third-Party Verification': 4,
            'Age Estimation': 3,
            'Parental Consent': 3,
            'Self-Attestation': 4,
            'Credit Card': 2,
            'Government ID': 1
        }
        return scores.get(method, 3)
    
    def _effectiveness_score(self, method):
        """Assign effectiveness score to age verification method"""
        scores = {
            'Privacy-Preserving': 4,
            'Third-Party Verification': 5,
            'Age Estimation': 3,
            'Parental Consent': 4,
            'Self-Attestation': 1,
            'Credit Card': 4,
            'Government ID': 5
        }
        return scores.get(method, 3)
    
    def generate_federal_recommendations(self):
        """Generate comprehensive federal policy recommendations"""
        print("\n" + "="*80)
        print("FEDERAL POLICY RECOMMENDATIONS")
        print("Based on State Legislative Analysis")
        print("="*80)
        
        recommendations = {
            'Federal Standards (Uniform Nationwide)': [
                'Age verification requirements for high-risk platforms',
                'Minimum data privacy protections for minors',
                'Platform liability framework for negligent harm',
                'Transparency and reporting requirements',
                'Prohibition on targeted advertising to minors'
            ],
            'Federal Framework with State Flexibility': [
                'Design standards and default settings (general principles)',
                'Parental consent mechanisms (implementation varies)',
                'Content moderation approaches (cultural context)',
                'Educational program requirements (local control)',
                'Enforcement mechanisms (state resources)'
            ],
            'Best Left to States': [
                'School-specific technology policies',
                'State consumer protection enforcement',
                'Local community standards for content',
                'State-level penalties and remedies',
                'Implementation timelines based on resources'
            ]
        }
        
        print("\n📋 RECOMMENDED FEDERAL-STATE DIVISION:")
        for category, items in recommendations.items():
            print(f"\n{category}:")
            for item in items:
                print(f"  • {item}")
        
        print("\n" + "="*80)
        print("Key Principles for Federal Legislation:")
        print("="*80)
        
        principles = {
            '1. Technology Neutrality': 'Set outcomes, not specific technologies',
            '2. Privacy by Design': 'Mandate privacy-preserving approaches',
            '3. Adaptability': 'Regular review and update mechanisms',
            '4. Proportionality': 'Match requirements to platform risk',
            '5. Preemption Balance': 'Federal floor, state ceiling allowed',
            '6. Enforcement Coordination': 'Federal-state cooperation framework'
        }
        
        for principle, description in principles.items():
            print(f"\n{principle}: {description}")
        
        return recommendations


def main():
    """Run comprehensive challenge analysis"""
    print("="*80)
    print("MIT HACKATHON CHALLENGE ANALYSIS")
    print("Youth Online Safety Standards: Federal Policy Development")
    print("Data-Driven Analysis from State Legislative Tracker")
    print("="*80)
    print()
    
    # Initialize analyzer
    passed_bills = "results/runs/run1_20251122_141346/passed_bills_detailed.csv"
    
    if not os.path.exists(passed_bills):
        print(f"Error: Could not find {passed_bills}")
        print("Please run the main policy_analysis.py script first.")
        return
    
    analyzer = ChallengeAnalyzer(passed_bills)
    
    # Run all analyses
    print("\nRunning comprehensive challenge analysis...\n")
    
    # Question 1: Holistic insights
    state_scores, dimensions = analyzer.analyze_holistic_patterns()
    
    # Question 2: State consensus
    provision_consensus, state_provisions = analyzer.analyze_state_consensus()
    
    # Question 3: Federalism balance
    federalism_recs, federal_candidates = analyzer.analyze_federalism_balance()
    
    # Question 4: Privacy + effectiveness
    age_methods, privacy_practices, effectiveness_features = analyzer.analyze_privacy_effectiveness()
    
    # Generate recommendations
    recommendations = analyzer.generate_federal_recommendations()
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll results saved to: {analyzer.output_dir}")
    print("\nGenerated Files:")
    print("  📊 Visualizations:")
    print("     - holistic_state_heatmap.png")
    print("     - consensus_analysis.png")
    print("     - federalism_analysis.png")
    print("     - privacy_effectiveness_analysis.png")
    print("\n  📋 Data Tables:")
    print("     - holistic_state_scores.csv")
    print("     - provision_consensus.csv")
    print("     - federalism_recommendations.csv")
    print("     - age_verification_methods.csv")
    print("     - best_practice_bills.csv")
    print("\n✅ Challenge questions answered with data-driven insights!")


if __name__ == "__main__":
    main()
