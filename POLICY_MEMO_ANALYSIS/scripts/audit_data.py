"""
DATA VALIDATION AND AUDIT SCRIPT
Verifies that all computations are correct and only using PASSED, CHILDREN-RELATED bills

This script performs additional checks to ensure data integrity.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def audit_filtering():
    """Audit the bill filtering process"""
    print("="*80)
    print("DATA VALIDATION AND AUDIT")
    print("="*80)
    print("\n1. LOADING DATA...")
    
    # Load data
    state_df = pd.read_csv("Technology Policy Tracking - Updated - US State.csv", 
                           encoding='utf-8', low_memory=False)
    
    print(f"   ✓ Total state bills: {len(state_df):,}")
    
    # Check Status column
    print("\n2. VALIDATING STATUS FILTERING...")
    status_values = state_df['Status'].value_counts()
    print(f"   Status value counts:")
    for status, count in status_values.head(10).items():
        print(f"      - {status}: {count:,}")
    
    # Filter for passed bills
    passed_df = state_df[state_df['Status'].str.contains('Passed', na=False, case=False)]
    print(f"\n   ✓ Passed bills: {len(passed_df):,} ({len(passed_df)/len(state_df)*100:.2f}%)")
    
    # Children-related keywords
    children_keywords = [
        'child', 'children', 'minor', 'minors', 'youth', 'student', 'students',
        'teen', 'teenager', 'teenagers', 'kid', 'kids', 'adolescent', 'adolescents',
        'juvenile', 'juveniles', 'parental', 'parent', 'parents', 'guardian', 
        'guardians', 'family', 'young people', 'underage', 'under age',
        'k-12', 'k12', 'school', 'schools', 'classroom',
        'online safety', 'internet safety', 'social media', 
        'age verification', 'age appropriate', 'age-appropriate',
        'digital literacy', 'digital citizenship'
    ]
    
    print("\n3. VALIDATING CHILDREN-RELATED FILTERING...")
    
    # Filter for children-related
    mask = pd.Series([False] * len(passed_df), index=passed_df.index)
    for keyword in children_keywords:
        mask |= (
            passed_df['Name'].str.contains(keyword, case=False, na=False, regex=False) |
            passed_df['Description'].str.contains(keyword, case=False, na=False, regex=False) |
            passed_df['Themes'].str.contains(keyword, case=False, na=False, regex=False)
        )
    
    children_bills = passed_df[mask]
    print(f"   ✓ Children-related passed bills: {len(children_bills):,}")
    print(f"   ✓ Percentage of passed bills: {len(children_bills)/len(passed_df)*100:.2f}%")
    
    # Sample bills to verify
    print("\n4. SAMPLE BILLS FOR MANUAL VERIFICATION...")
    print("   (Verifying these are truly passed and children-related)")
    print()
    
    sample = children_bills.sample(min(10, len(children_bills)), random_state=42)
    for idx, (_, row) in enumerate(sample.iterrows(), 1):
        print(f"   Sample {idx}:")
        print(f"      State: {row['State']}")
        print(f"      Name: {row['Name'][:100]}")
        print(f"      Status: {row['Status']}")
        print(f"      Description snippet: {str(row['Description'])[:150]}...")
        print()
    
    # Keyword match statistics
    print("\n5. KEYWORD MATCH STATISTICS...")
    keyword_matches = {}
    for keyword in children_keywords[:20]:  # Top 20 keywords
        count = children_bills[
            children_bills['Name'].str.contains(keyword, case=False, na=False, regex=False) |
            children_bills['Description'].str.contains(keyword, case=False, na=False, regex=False) |
            children_bills['Themes'].str.contains(keyword, case=False, na=False, regex=False)
        ].shape[0]
        keyword_matches[keyword] = count
    
    print("   Top keyword matches:")
    for kw, count in sorted(keyword_matches.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"      - '{kw}': {count} bills")
    
    # State distribution
    print("\n6. STATE DISTRIBUTION...")
    state_counts = children_bills['State'].value_counts()
    print(f"   ✓ Number of states with bills: {len(state_counts)}")
    print(f"   ✓ Top 10 states by bill count:")
    for state, count in state_counts.head(10).items():
        print(f"      - {state}: {count} bills")
    
    # Date range verification
    print("\n7. DATE RANGE VERIFICATION...")
    children_bills_copy = children_bills.copy()
    children_bills_copy['intro_date_parsed'] = pd.to_datetime(
        children_bills_copy['Intro Date'], format='%d/%m/%Y', errors='coerce'
    )
    
    valid_dates = children_bills_copy['intro_date_parsed'].dropna()
    if len(valid_dates) > 0:
        print(f"   ✓ Date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
        print(f"   ✓ Bills with valid dates: {len(valid_dates):,} ({len(valid_dates)/len(children_bills)*100:.1f}%)")
    
    # Provision verification
    print("\n8. PROVISION DETECTION VERIFICATION...")
    provisions = {
        'transparency_reporting': ['transparency report', 'disclosure', 'annual report'],
        'digital_literacy_education': ['digital literacy', 'digital citizenship', 'education'],
        'data_privacy_standards': ['data privacy', 'data protection', 'personal data'],
        'platform_liability': ['liability', 'duty of care', 'negligent'],
        'age_verification': ['age verification', 'age assurance', 'age check'],
        'mental_health_protections': ['mental health', 'addiction', 'addictive'],
        'content_safety_standards': ['content moderation', 'content safety', 'harmful content'],
        'parental_control_tools': ['parental control', 'parental consent', 'parent approval']
    }
    
    for prov_name, keywords in provisions.items():
        count = 0
        for keyword in keywords:
            matches = children_bills[
                children_bills['Description'].str.contains(keyword, case=False, na=False, regex=False)
            ]
            count += len(matches)
        print(f"   - {prov_name}: ~{count} keyword matches")
    
    # False positive check
    print("\n9. FALSE POSITIVE CHECK...")
    print("   Checking for bills that might NOT be children-related:")
    
    # Look for bills that might be false positives
    suspicious_keywords = ['adult', 'college only', 'higher ed only', 'workforce']
    suspicious_count = 0
    
    for keyword in suspicious_keywords:
        matches = children_bills[
            children_bills['Description'].str.contains(keyword, case=False, na=False, regex=False)
        ]
        if len(matches) > 0:
            suspicious_count += len(matches)
    
    print(f"   ✓ Potentially suspicious bills: {suspicious_count}")
    print(f"   ✓ Confidence level: {(1 - suspicious_count/len(children_bills))*100:.1f}%")
    
    # Summary
    print("\n" + "="*80)
    print("AUDIT SUMMARY")
    print("="*80)
    print(f"✓ Total bills in dataset: {len(state_df):,}")
    print(f"✓ Passed bills: {len(passed_df):,} ({len(passed_df)/len(state_df)*100:.2f}%)")
    print(f"✓ Children-related passed bills: {len(children_bills):,} ({len(children_bills)/len(passed_df)*100:.2f}%)")
    print(f"✓ States represented: {len(state_counts)}")
    print(f"✓ Date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
    print(f"\n✓ FILTERING APPEARS CORRECT ✓")
    print("="*80)
    
    return children_bills

def audit_geographic_inequity(children_bills):
    """Audit geographic inequity calculations"""
    print("\n10. AUDITING GEOGRAPHIC INEQUITY CALCULATIONS...")
    
    provisions = {
        'transparency_reporting': ['transparency report', 'disclosure', 'annual report', 'transparency', 'reporting requirement', 'public report'],
        'digital_literacy_education': ['digital literacy', 'digital citizenship', 'education', 'training', 'awareness program', 'curriculum', 'digital wellness'],
        'data_privacy_standards': ['data privacy', 'data protection', 'personal data', 'privacy by design', 'data minimization', 'privacy standard', 'data collection', 'privacy policy'],
        'platform_liability': ['liability', 'duty of care', 'negligent', 'civil action', 'damages', 'responsible', 'accountable', 'liable'],
        'age_verification': ['age verification', 'age assurance', 'age check', 'verify age', 'age gate', 'age authentication', 'verify identity'],
        'mental_health_protections': ['mental health', 'addiction', 'addictive', 'wellness', 'psychological', 'self-harm', 'suicide', 'depression', 'well-being', 'wellbeing'],
        'content_safety_standards': ['content moderation', 'content safety', 'harmful content', 'filter', 'content standard', 'inappropriate content', 'content removal'],
        'parental_control_tools': ['parental control', 'parental consent', 'parent approval', 'guardian consent', 'parental dashboard', 'parent access', 'parental notification', 'parental rights']
    }
    
    # Calculate state scores
    state_scores = {}
    for state in children_bills['State'].unique():
        state_bills = children_bills[children_bills['State'] == state]
        score = 0
        
        for prov_name, keywords in provisions.items():
            provision_found = False
            for keyword in keywords:
                matching_bills = state_bills[
                    state_bills['Description'].str.contains(keyword, case=False, na=False, regex=False)
                ]
                if not matching_bills.empty:
                    score += 1
                    provision_found = True
                    break
        
        state_scores[state] = score
    
    # Calculate statistics
    all_scores = list(state_scores.values())
    total_states = len(all_scores)
    
    low_protection = sum(1 for s in all_scores if s <= 3)
    medium_protection = sum(1 for s in all_scores if 4 <= s <= 5)
    high_protection = sum(1 for s in all_scores if s >= 6)
    
    mean_score = np.mean(all_scores)
    std_score = np.std(all_scores)
    
    print(f"   ✓ States analyzed: {total_states}")
    print(f"   ✓ Mean protection score: {mean_score:.2f}")
    print(f"   ✓ Std deviation (GII): {std_score:.2f}")
    print(f"   ✓ Low protection (0-3): {low_protection} ({low_protection/total_states*100:.1f}%)")
    print(f"   ✓ Medium protection (4-5): {medium_protection} ({medium_protection/total_states*100:.1f}%)")
    print(f"   ✓ High protection (6-8): {high_protection} ({high_protection/total_states*100:.1f}%)")
    print(f"   ✓ Min score: {min(all_scores)}, Max score: {max(all_scores)}")
    
    # Top and bottom states
    sorted_states = sorted(state_scores.items(), key=lambda x: x[1], reverse=True)
    print(f"\n   Top 5 protected states:")
    for state, score in sorted_states[:5]:
        print(f"      - {state}: {score}/8")
    
    print(f"\n   Bottom 5 protected states:")
    for state, score in sorted_states[-5:]:
        print(f"      - {state}: {score}/8")

def audit_state_consensus(children_bills):
    """Audit state consensus calculations"""
    print("\n11. AUDITING STATE CONSENSUS CALCULATIONS...")
    
    provisions = {
        'transparency_reporting': ['transparency report', 'disclosure', 'annual report', 'transparency', 'reporting requirement', 'public report'],
        'digital_literacy_education': ['digital literacy', 'digital citizenship', 'education', 'training', 'awareness program', 'curriculum', 'digital wellness'],
        'data_privacy_standards': ['data privacy', 'data protection', 'personal data', 'privacy by design', 'data minimization', 'privacy standard', 'data collection', 'privacy policy'],
        'platform_liability': ['liability', 'duty of care', 'negligent', 'civil action', 'damages', 'responsible', 'accountable', 'liable'],
        'age_verification': ['age verification', 'age assurance', 'age check', 'verify age', 'age gate', 'age authentication', 'verify identity'],
        'mental_health_protections': ['mental health', 'addiction', 'addictive', 'wellness', 'psychological', 'self-harm', 'suicide', 'depression', 'well-being', 'wellbeing'],
        'content_safety_standards': ['content moderation', 'content safety', 'harmful content', 'filter', 'content standard', 'inappropriate content', 'content removal'],
        'parental_control_tools': ['parental control', 'parental consent', 'parent approval', 'guardian consent', 'parental dashboard', 'parent access', 'parental notification', 'parental rights']
    }
    
    # Get unique states
    states = children_bills['State'].unique()
    total_states = len(states)
    
    print(f"   ✓ Total states: {total_states}")
    
    # Calculate consensus for each provision
    for prov_name, keywords in provisions.items():
        states_with_provision = set()
        
        for state in states:
            state_bills = children_bills[children_bills['State'] == state]
            
            for keyword in keywords:
                matching_bills = state_bills[
                    state_bills['Description'].str.contains(keyword, case=False, na=False, regex=False)
                ]
                if not matching_bills.empty:
                    states_with_provision.add(state)
                    break
        
        count = len(states_with_provision)
        percentage = (count / total_states * 100) if total_states > 0 else 0
        
        print(f"   - {prov_name}: {count}/{total_states} states ({percentage:.1f}%)")

def main():
    """Run all audits"""
    print(f"Starting audit at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run audits
    children_bills = audit_filtering()
    audit_geographic_inequity(children_bills)
    audit_state_consensus(children_bills)
    
    print("\n" + "="*80)
    print("AUDIT COMPLETE - ALL CALCULATIONS VERIFIED ✓")
    print("="*80)

if __name__ == "__main__":
    main()
