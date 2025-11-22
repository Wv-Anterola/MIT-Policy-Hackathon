"""
Comprehensive Technology Policy Analysis Script
Children's Online Safety Legislation - State & Federal Analysis

Combines all analysis capabilities:
- Advanced NLP analysis of state bills
- Challenge-focused analysis for federal policy development
- Federal data integration for comprehensive insights
- Baseline "floor" establishment from state legislation

Version: 3.0 - Comprehensive Edition
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import re
from wordcloud import WordCloud
import warnings
import os
import sys
import argparse
import logging
import time
from datetime import datetime
from pathlib import Path
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy
from textblob import TextBlob
from tqdm import tqdm
import json
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_analysis.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    print("Downloading spaCy language model...")
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Set visualization style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


class ComprehensivePolicyAnalyzer:
    """
    Comprehensive analyzer combining state & federal policy analysis
    with advanced NLP and challenge-focused insights
    """
    
    def __init__(self, state_csv_path, federal_csv_path=None, output_dir=None, 
                 states_filter=None, date_range=None, verbose=True):
        """Initialize with state and federal data"""
        logging.info("Initializing ComprehensivePolicyAnalyzer...")
        self.verbose = verbose
        
        # Load state data
        try:
            self.state_df = pd.read_csv(state_csv_path)
            logging.info(f"Loaded {len(self.state_df)} state bills")
            
            if states_filter:
                self.state_df = self.state_df[self.state_df['State'].isin(states_filter)]
                logging.info(f"Filtered to {len(states_filter)} states")
            
            if date_range:
                self.state_df['Intro Date'] = pd.to_datetime(
                    self.state_df['Intro Date'], format='%d/%m/%Y', errors='coerce'
                )
                start, end = date_range
                self.state_df = self.state_df[
                    (self.state_df['Intro Date'] >= start) & 
                    (self.state_df['Intro Date'] <= end)
                ]
                logging.info(f"Filtered to date range: {start} to {end}")
                
        except Exception as e:
            logging.error(f"Error loading state data: {e}")
            raise
        
        # Load federal data if provided
        self.federal_df = None
        if federal_csv_path and os.path.exists(federal_csv_path):
            try:
                self.federal_df = pd.read_csv(federal_csv_path)
                logging.info(f"Loaded {len(self.federal_df)} federal bills")
            except Exception as e:
                logging.warning(f"Could not load federal data: {e}")
        
        self.children_related_df = None
        self.federal_children_df = None
        self.output_dir = output_dir or self._create_run_directory()
        
        # Initialize NLP components
        logging.info("Initializing NLP components...")
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.tfidf_vectorizer = TfidfVectorizer(max_features=100, ngram_range=(1, 3))
        
        # Statistics tracking
        self.stats = {
            'processing_time': {},
            'data_quality': {},
            'errors': []
        }
    
    def _create_run_directory(self):
        """Create organized directory structure"""
        base_dir = "comprehensive_results"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_dir = os.path.join(base_dir, f"analysis_{timestamp}")
        os.makedirs(run_dir, exist_ok=True)
        print(f"Created output directory: {run_dir}\n")
        return run_dir
    
    def _save_plot(self, filename):
        """Save plot to output directory"""
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        return filepath
    
    def _save_csv(self, df, filename):
        """Save dataframe to CSV"""
        filepath = os.path.join(self.output_dir, filename)
        if isinstance(df, pd.DataFrame):
            df.to_csv(filepath, index=True)
        elif isinstance(df, pd.Series):
            df.to_csv(filepath)
        return filepath
    
    def _preprocess_text(self, text):
        """Advanced text preprocessing"""
        if pd.isna(text):
            return ""
        try:
            tokens = word_tokenize(str(text).lower())
            processed_tokens = [
                self.lemmatizer.lemmatize(token) 
                for token in tokens 
                if token.isalpha() and token not in self.stop_words and len(token) > 2
            ]
            return ' '.join(processed_tokens)
        except Exception as e:
            logging.warning(f"Text preprocessing error: {e}")
            return str(text).lower()
    
    def _perform_sentiment_analysis(self, text):
        """Sentiment analysis on text"""
        if pd.isna(text):
            return {'polarity': 0.0, 'subjectivity': 0.0}
        try:
            blob = TextBlob(str(text))
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            return {'polarity': 0.0, 'subjectivity': 0.0}
    
    # ========================================================================
    # PART 1: STATE BILL IDENTIFICATION & ANALYSIS
    # ========================================================================
    
    def identify_children_related_bills(self):
        """Identify children-related bills using advanced NLP"""
        start_time = time.time()
        logging.info("Starting NLP analysis for children-related bills...")
        
        children_keywords = [
            'children', 'child', 'minor', 'minors', 'student', 'students',
            'kids', 'youth', 'juvenile', 'adolescent', 'teen', 'teenager',
            'parental', 'parent', 'guardian', 'family', 'school', 'k-12',
            'age verification', 'age-verification', 'underage', 'young people'
        ]
        
        safety_keywords = [
            'safety', 'protect', 'protection', 'secure', 'security',
            'privacy', 'harmful', 'abuse', 'exploitation', 'predator'
        ]
        
        tech_keywords = [
            'online', 'internet', 'social media', 'platform', 'digital',
            'website', 'app', 'device', 'screen', 'cyber'
        ]
        
        children_pattern = '|'.join(children_keywords)
        safety_pattern = '|'.join(safety_keywords)
        tech_pattern = '|'.join(tech_keywords)
        
        self.state_df['children_score'] = 0.0
        
        for idx, row in self.state_df.iterrows():
            score = 0
            
            if pd.notna(row['Name']) and re.search(children_pattern, str(row['Name']), re.IGNORECASE):
                score += 3
            if pd.notna(row['Description']) and re.search(children_pattern, str(row['Description']), re.IGNORECASE):
                score += 2
            if pd.notna(row['Themes']) and re.search(children_pattern, str(row['Themes']), re.IGNORECASE):
                score += 2
            
            combined_text = f"{row['Name']} {row['Description']} {row['Themes']}"
            if re.search(safety_pattern, combined_text, re.IGNORECASE):
                score += 1
            if re.search(tech_pattern, combined_text, re.IGNORECASE):
                score += 1
            
            if pd.notna(row['Themes']):
                if 'Children' in str(row['Themes']):
                    score += 3
                if 'Online Safety' in str(row['Themes']):
                    score += 2
            
            self.state_df.at[idx, 'children_score'] = score
        
        self.state_df['is_children_related'] = self.state_df['children_score'] >= 3
        
        # Preprocess text
        if self.verbose:
            print("Preprocessing text...")
        self.state_df['processed_description'] = self.state_df['Description'].apply(
            self._preprocess_text
        )
        
        # Sentiment analysis
        if self.verbose:
            print("Performing sentiment analysis...")
        sentiments = self.state_df['Description'].apply(self._perform_sentiment_analysis)
        self.state_df['sentiment_polarity'] = sentiments.apply(lambda x: x['polarity'])
        self.state_df['sentiment_subjectivity'] = sentiments.apply(lambda x: x['subjectivity'])
        
        self.children_related_df = self.state_df[self.state_df['is_children_related']].copy()
        
        elapsed = time.time() - start_time
        self.stats['processing_time']['identify_children_related_bills'] = elapsed
        
        logging.info(f"Identified {len(self.children_related_df)} children-related state bills ({elapsed:.2f}s)")
        
        # Also analyze federal bills if available
        if self.federal_df is not None:
            self._identify_federal_children_bills()
        
        return self.children_related_df
    
    def _identify_federal_children_bills(self):
        """Identify children-related federal bills"""
        if self.federal_df is None:
            return None
        
        logging.info("Analyzing federal bills for children-related content...")
        
        children_pattern = 'children|child|minor|minors|youth|student|parental|parent|guardian|young people'
        
        self.federal_df['children_score'] = 0
        for idx, row in self.federal_df.iterrows():
            score = 0
            if pd.notna(row['Name']) and re.search(children_pattern, str(row['Name']), re.IGNORECASE):
                score += 3
            if pd.notna(row.get('Description', '')) and re.search(children_pattern, str(row.get('Description', '')), re.IGNORECASE):
                score += 2
            if pd.notna(row.get('Themes', '')) and re.search(children_pattern, str(row.get('Themes', '')), re.IGNORECASE):
                score += 2
            self.federal_df.at[idx, 'children_score'] = score
        
        self.federal_df['is_children_related'] = self.federal_df['children_score'] >= 3
        self.federal_children_df = self.federal_df[self.federal_df['is_children_related']].copy()
        
        logging.info(f"Identified {len(self.federal_children_df)} children-related federal bills")
        return self.federal_children_df
    
    # ========================================================================
    # PART 2: STATE ANALYSIS (STATUS, THEMES, TEMPORAL, PROVISIONS)
    # ========================================================================
    
    def analyze_state_bills(self):
        """Comprehensive state bill analysis"""
        if self.children_related_df is None:
            self.identify_children_related_bills()
        
        print("\n" + "="*80)
        print("STATE LEGISLATION ANALYSIS")
        print("="*80)
        
        # Status analysis
        status_counts = self.children_related_df['Status'].value_counts()
        print(f"\n{'Status':<20} {'Count':<10} {'Percentage'}")
        print("-"*50)
        for status, count in status_counts.items():
            pct = (count / len(self.children_related_df)) * 100
            print(f"{status:<20} {count:<10} {pct:.1f}%")
        
        # State-by-state analysis
        state_counts = self.children_related_df['State'].value_counts()
        passed_bills = self.children_related_df[self.children_related_df['Status'] == 'Passed']
        passed_by_state = passed_bills['State'].value_counts()
        
        state_summary = pd.DataFrame({
            'Total Bills': state_counts,
            'Passed Bills': passed_by_state
        }).fillna(0).astype(int)
        state_summary['Pass Rate (%)'] = (
            (state_summary['Passed Bills'] / state_summary['Total Bills'] * 100).round(2)
        )
        
        print(f"\n\nTop 15 States by Activity:")
        print(f"{'State':<20} {'Total':<10} {'Passed':<10} {'Pass Rate'}")
        print("-"*60)
        for state, row in state_summary.head(15).iterrows():
            print(f"{state:<20} {row['Total Bills']:<10} {row['Passed Bills']:<10} {row['Pass Rate (%)']:.1f}%")
        
        # Theme analysis
        all_themes = []
        for themes_str in self.children_related_df['Themes'].dropna():
            themes = [t.strip() for t in themes_str.split(',')]
            all_themes.extend(themes)
        
        theme_counts = Counter(all_themes)
        print(f"\n\nTop 10 Themes:")
        print(f"{'Theme':<40} {'Count'}")
        print("-"*60)
        for theme, count in theme_counts.most_common(10):
            print(f"{theme:<40} {count}")
        
        # Save data
        self._save_csv(status_counts.to_frame('Count'), 'state_status_analysis.csv')
        self._save_csv(state_summary, 'state_by_state_analysis.csv')
        
        # Visualizations
        self._create_state_visualizations(status_counts, state_summary, theme_counts)
        
        return status_counts, state_summary, theme_counts
    
    def _create_state_visualizations(self, status_counts, state_summary, theme_counts):
        """Create comprehensive state visualizations - ENHANCED VERSION"""
        
        # 1. Status distribution (original)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        status_counts.plot(kind='bar', ax=ax1, color='steelblue', edgecolor='black')
        ax1.set_title('State Bills by Status', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Status')
        ax1.set_ylabel('Number of Bills')
        ax1.tick_params(axis='x', rotation=45)
        for i, v in enumerate(status_counts.values):
            ax1.text(i, v + max(status_counts.values)*0.01, str(v), ha='center', fontweight='bold')
        
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
        ax2.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%',
                startangle=90, colors=colors, textprops={'fontweight': 'bold'})
        ax2.set_title('Distribution of Bill Status', fontweight='bold')
        plt.tight_layout()
        self._save_plot('state_status_distribution.png')
        
        # 2. Top states (enhanced with pass rate)
        fig, ax = plt.subplots(figsize=(14, 8))
        top_states = state_summary.head(20)
        x = np.arange(len(top_states))
        width = 0.35
        ax.bar(x - width/2, top_states['Total Bills'], width, label='Total Bills', 
               color='skyblue', edgecolor='black')
        ax.bar(x + width/2, top_states['Passed Bills'], width, label='Passed Bills',
               color='lightgreen', edgecolor='black')
        ax.set_xlabel('State', fontweight='bold')
        ax.set_ylabel('Number of Bills', fontweight='bold')
        ax.set_title('Top 20 States: Children\'s Online Safety Legislation', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(top_states.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        self._save_plot('state_top_states.png')
        
        # 3. NEW: Pass rate ranking
        fig, ax = plt.subplots(figsize=(12, 10))
        state_with_bills = state_summary[state_summary['Total Bills'] >= 3].sort_values('Pass Rate (%)', ascending=True)
        top_pass_rate = state_with_bills.tail(20)
        colors_pass = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(top_pass_rate)))
        bars = ax.barh(top_pass_rate.index, top_pass_rate['Pass Rate (%)'], color=colors_pass, edgecolor='black')
        ax.set_xlabel('Pass Rate (%)', fontweight='bold', fontsize=12)
        ax.set_title('Top 20 States by Legislative Success Rate\n(Minimum 3 Bills)', 
                    fontweight='bold', fontsize=14)
        ax.grid(axis='x', alpha=0.3)
        for i, (idx, row) in enumerate(top_pass_rate.iterrows()):
            ax.text(row['Pass Rate (%)'] + 1, i, f"{row['Pass Rate (%)']:.1f}% ({int(row['Passed Bills'])}/{int(row['Total Bills'])})", 
                   va='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        self._save_plot('state_pass_rate_ranking.png')
        
        # 4. NEW: State activity heatmap by region
        fig, ax = plt.subplots(figsize=(14, 8))
        regions = {
            'West Coast': ['California', 'Oregon', 'Washington', 'Nevada'],
            'Southwest': ['Arizona', 'New Mexico', 'Texas', 'Oklahoma'],
            'Midwest': ['Illinois', 'Michigan', 'Ohio', 'Wisconsin', 'Minnesota', 'Indiana', 'Missouri', 'Iowa'],
            'Northeast': ['New York', 'Massachusetts', 'Connecticut', 'Vermont', 'New Jersey', 'Pennsylvania', 'Maine', 'Rhode Island'],
            'Southeast': ['Florida', 'Georgia', 'North Carolina', 'South Carolina', 'Virginia', 'Tennessee', 'Alabama', 'Louisiana'],
            'Mountain': ['Colorado', 'Utah', 'Montana', 'Idaho', 'Wyoming']
        }
        
        region_data = {}
        for region, states in regions.items():
            region_bills = state_summary[state_summary.index.isin(states)]
            if len(region_bills) > 0:
                region_data[region] = {
                    'Total': region_bills['Total Bills'].sum(),
                    'Passed': region_bills['Passed Bills'].sum(),
                    'States Active': len(region_bills),
                    'Avg per State': region_bills['Total Bills'].mean()
                }
        
        region_df = pd.DataFrame(region_data).T
        x_pos = np.arange(len(region_df))
        width = 0.35
        ax.bar(x_pos - width/2, region_df['Total'], width, label='Total Bills', color='#3498db', edgecolor='black')
        ax.bar(x_pos + width/2, region_df['Passed'], width, label='Passed Bills', color='#2ecc71', edgecolor='black')
        ax.set_xlabel('Region', fontweight='bold', fontsize=12)
        ax.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax.set_title('Regional Legislative Activity Analysis', fontweight='bold', fontsize=14)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(region_df.index, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        for i, v in enumerate(region_df['Total']):
            ax.text(i - width/2, v + max(region_df['Total'])*0.02, str(int(v)), ha='center', fontweight='bold', fontsize=9)
        for i, v in enumerate(region_df['Passed']):
            ax.text(i + width/2, v + max(region_df['Total'])*0.02, str(int(v)), ha='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        self._save_plot('state_regional_activity.png')
        
        # 5. NEW: Theme bar chart (top 20)
        fig, ax = plt.subplots(figsize=(12, 10))
        top_themes = dict(theme_counts.most_common(20))
        theme_names = list(top_themes.keys())
        theme_values = list(top_themes.values())
        colors_theme = plt.cm.viridis(np.linspace(0.2, 0.95, len(theme_names)))
        bars = ax.barh(range(len(theme_names)), theme_values, color=colors_theme, edgecolor='black')
        ax.set_yticks(range(len(theme_names)))
        ax.set_yticklabels(theme_names, fontsize=10)
        ax.set_xlabel('Number of Bills', fontweight='bold', fontsize=12)
        ax.set_title('Top 20 Policy Themes in State Legislation', fontweight='bold', fontsize=14)
        ax.grid(axis='x', alpha=0.3)
        ax.invert_yaxis()
        for i, v in enumerate(theme_values):
            ax.text(v + max(theme_values)*0.01, i, str(v), va='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        self._save_plot('state_themes_bar_chart.png')
        
        # 6. Themes word cloud (original)
        fig, ax = plt.subplots(figsize=(14, 8))
        wordcloud = WordCloud(width=800, height=600, background_color='white',
                             colormap='viridis').generate_from_frequencies(theme_counts)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        ax.set_title('State Bill Themes Word Cloud', fontsize=16, fontweight='bold')
        plt.tight_layout()
        self._save_plot('state_themes_wordcloud.png')
        
        # 7. NEW: Sentiment analysis visualization
        if 'sentiment_polarity' in self.children_related_df.columns:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            
            # Sentiment distribution
            sentiment_data = self.children_related_df['sentiment_polarity'].dropna()
            ax1.hist(sentiment_data, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
            ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Neutral')
            ax1.axvline(x=sentiment_data.mean(), color='green', linestyle='--', linewidth=2, label=f'Mean: {sentiment_data.mean():.3f}')
            ax1.set_xlabel('Sentiment Polarity', fontweight='bold')
            ax1.set_ylabel('Number of Bills', fontweight='bold')
            ax1.set_title('Bill Language Sentiment Distribution\n(-1=Negative, 0=Neutral, +1=Positive)', fontweight='bold')
            ax1.legend()
            ax1.grid(axis='y', alpha=0.3)
            
            # Sentiment by status
            status_sentiment = self.children_related_df.groupby('Status')['sentiment_polarity'].mean().sort_values()
            colors_sent = ['red' if v < 0 else 'yellow' if v < 0.1 else 'green' for v in status_sentiment.values]
            ax2.barh(status_sentiment.index, status_sentiment.values, color=colors_sent, edgecolor='black')
            ax2.axvline(x=0, color='black', linestyle='-', linewidth=1)
            ax2.set_xlabel('Average Sentiment Polarity', fontweight='bold')
            ax2.set_title('Average Bill Sentiment by Status', fontweight='bold')
            ax2.grid(axis='x', alpha=0.3)
            for i, v in enumerate(status_sentiment.values):
                ax2.text(v + 0.01 if v > 0 else v - 0.01, i, f'{v:.3f}', 
                        va='center', ha='left' if v > 0 else 'right', fontweight='bold')
            
            plt.tight_layout()
            self._save_plot('state_sentiment_analysis.png')
        
        # 8. NEW: Timeline analysis
        if 'Intro Date' in self.children_related_df.columns:
            self.children_related_df['Year'] = pd.to_datetime(
                self.children_related_df['Intro Date'], format='%d/%m/%Y', errors='coerce'
            ).dt.year
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
            
            # Bills over time
            yearly = self.children_related_df.groupby('Year').size().sort_index()
            yearly_passed = self.children_related_df[self.children_related_df['Status'] == 'Passed'].groupby('Year').size()
            
            ax1.plot(yearly.index, yearly.values, marker='o', linewidth=3, markersize=10, 
                    label='Total Bills', color='#3498db', markeredgecolor='black', markeredgewidth=2)
            ax1.plot(yearly_passed.index, yearly_passed.values, marker='s', linewidth=3, markersize=10,
                    label='Passed Bills', color='#2ecc71', markeredgecolor='black', markeredgewidth=2)
            ax1.fill_between(yearly.index, yearly.values, alpha=0.3, color='#3498db')
            ax1.fill_between(yearly_passed.index, yearly_passed.values, alpha=0.3, color='#2ecc71')
            ax1.set_xlabel('Year', fontweight='bold', fontsize=12)
            ax1.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
            ax1.set_title('Legislative Activity Timeline: Children\'s Online Safety', fontweight='bold', fontsize=14)
            ax1.legend(fontsize=11)
            ax1.grid(True, alpha=0.3)
            
            # Success rate over time
            yearly_rate = (yearly_passed / yearly * 100).fillna(0)
            colors_timeline = ['red' if v < 20 else 'orange' if v < 40 else 'green' for v in yearly_rate.values]
            ax2.bar(yearly_rate.index, yearly_rate.values, color=colors_timeline, edgecolor='black', alpha=0.7)
            ax2.set_xlabel('Year', fontweight='bold', fontsize=12)
            ax2.set_ylabel('Pass Rate (%)', fontweight='bold', fontsize=12)
            ax2.set_title('Legislative Success Rate by Year', fontweight='bold', fontsize=14)
            ax2.grid(axis='y', alpha=0.3)
            for i, (year, rate) in enumerate(yearly_rate.items()):
                if not np.isnan(rate):
                    ax2.text(year, rate + 2, f'{rate:.1f}%', ha='center', fontweight='bold', fontsize=9)
            
            plt.tight_layout()
            self._save_plot('state_timeline_trends.png')
        
        # 9. NEW: State efficiency matrix (bills vs success)
        fig, ax = plt.subplots(figsize=(14, 10))
        scatter_data = state_summary[state_summary['Total Bills'] >= 2]
        sizes = scatter_data['Total Bills'] * 20
        colors_scatter = scatter_data['Pass Rate (%)']
        
        scatter = ax.scatter(scatter_data['Total Bills'], scatter_data['Pass Rate (%)'], 
                           s=sizes, c=colors_scatter, cmap='RdYlGn', alpha=0.6, 
                           edgecolors='black', linewidth=2)
        
        # Add state labels for notable states
        for state, row in scatter_data.iterrows():
            if row['Total Bills'] >= 10 or row['Pass Rate (%)'] >= 40:
                ax.annotate(state, (row['Total Bills'], row['Pass Rate (%)']), 
                          fontsize=9, fontweight='bold', alpha=0.7)
        
        ax.set_xlabel('Total Bills Introduced', fontweight='bold', fontsize=12)
        ax.set_ylabel('Pass Rate (%)', fontweight='bold', fontsize=12)
        ax.set_title('State Legislative Efficiency Matrix\n(Size = Number of Bills)', 
                    fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Pass Rate (%)', fontweight='bold')
        
        # Add quadrant lines
        median_bills = scatter_data['Total Bills'].median()
        median_rate = scatter_data['Pass Rate (%)'].median()
        ax.axhline(y=median_rate, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        ax.axvline(x=median_bills, color='gray', linestyle='--', alpha=0.5, linewidth=1)
        
        # Add quadrant labels
        ax.text(ax.get_xlim()[1]*0.95, median_rate + (ax.get_ylim()[1]-median_rate)*0.5, 
               'High Volume\nHigh Success', ha='right', va='center', 
               fontsize=10, style='italic', alpha=0.5, fontweight='bold')
        ax.text(ax.get_xlim()[0]*1.05, median_rate + (ax.get_ylim()[1]-median_rate)*0.5,
               'Low Volume\nHigh Success', ha='left', va='center',
               fontsize=10, style='italic', alpha=0.5, fontweight='bold')
        
        plt.tight_layout()
        self._save_plot('state_efficiency_matrix.png')
    
    # ========================================================================
    # PART 3: FEDERAL DATA ANALYSIS
    # ========================================================================
    
    def analyze_federal_bills(self):
        """Analyze federal bills for comparison with state efforts"""
        if self.federal_df is None:
            print("\nNo federal data available for analysis")
            return None
        
        if self.federal_children_df is None:
            self._identify_federal_children_bills()
        
        print("\n" + "="*80)
        print("FEDERAL LEGISLATION ANALYSIS")
        print("="*80)
        
        print(f"\nTotal federal bills analyzed: {len(self.federal_df)}")
        print(f"Children-related federal bills: {len(self.federal_children_df)}")
        
        if len(self.federal_children_df) == 0:
            print("No children-related federal bills found")
            return None
        
        # Status analysis
        if 'Status' in self.federal_children_df.columns:
            fed_status = self.federal_children_df['Status'].value_counts()
            print(f"\n{'Status':<25} {'Count'}")
            print("-"*40)
            for status, count in fed_status.items():
                print(f"{status:<25} {count}")
        
        # Themes analysis
        if 'Themes' in self.federal_children_df.columns:
            fed_themes = []
            for themes_str in self.federal_children_df['Themes'].dropna():
                themes = [t.strip() for t in str(themes_str).split(',')]
                fed_themes.extend(themes)
            
            fed_theme_counts = Counter(fed_themes)
            print(f"\n\nTop Federal Themes:")
            print(f"{'Theme':<40} {'Count'}")
            print("-"*60)
            for theme, count in fed_theme_counts.most_common(10):
                print(f"{theme:<40} {count}")
        
        # List key federal bills
        print(f"\n\nKey Federal Children's Safety Bills:")
        print("-"*80)
        for idx, row in self.federal_children_df.head(10).iterrows():
            print(f"\n📋 {row['Name']}")
            if 'Status' in row:
                print(f"   Status: {row['Status']}")
            if 'Themes' in row and pd.notna(row['Themes']):
                print(f"   Themes: {row['Themes']}")
        
        # Save federal analysis
        if 'Status' in self.federal_children_df.columns:
            self._save_csv(fed_status.to_frame('Count'), 'federal_status_analysis.csv')
        
        # Create federal visualizations - ENHANCED
        if 'Status' in self.federal_children_df.columns:
            # Federal status distribution
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
            fed_status.plot(kind='bar', ax=ax1, color='darkblue', edgecolor='black', alpha=0.8)
            ax1.set_title('Federal Children\'s Safety Bills by Status', 
                        fontsize=14, fontweight='bold')
            ax1.set_xlabel('Status', fontweight='bold')
            ax1.set_ylabel('Number of Bills', fontweight='bold')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(axis='y', alpha=0.3)
            for i, v in enumerate(fed_status.values):
                ax1.text(i, v + max(fed_status.values)*0.02, str(v), ha='center', fontweight='bold')
            
            # Federal pie chart
            colors_fed = ['#27ae60', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
            ax2.pie(fed_status.values, labels=fed_status.index, autopct='%1.1f%%',
                   startangle=90, colors=colors_fed, textprops={'fontweight': 'bold'})
            ax2.set_title('Federal Bill Status Distribution', fontweight='bold')
            
            plt.tight_layout()
            self._save_plot('federal_status_distribution.png')
            
            # NEW: Federal themes analysis
            if 'Themes' in self.federal_children_df.columns:
                fed_themes = []
                for themes_str in self.federal_children_df['Themes'].dropna():
                    themes = [t.strip() for t in str(themes_str).split(',')]
                    fed_themes.extend(themes)
                
                if len(fed_themes) > 0:
                    fed_theme_counts = Counter(fed_themes)
                    
                    fig, ax = plt.subplots(figsize=(12, 8))
                    top_fed_themes = dict(fed_theme_counts.most_common(15))
                    theme_names = list(top_fed_themes.keys())
                    theme_values = list(top_fed_themes.values())
                    colors_theme = plt.cm.plasma(np.linspace(0.2, 0.9, len(theme_names)))
                    
                    bars = ax.barh(range(len(theme_names)), theme_values, 
                                  color=colors_theme, edgecolor='black', alpha=0.8)
                    ax.set_yticks(range(len(theme_names)))
                    ax.set_yticklabels(theme_names, fontsize=10)
                    ax.set_xlabel('Number of Bills', fontweight='bold', fontsize=12)
                    ax.set_title('Federal Policy Focus Areas\n(Top 15 Themes)', 
                               fontweight='bold', fontsize=14)
                    ax.grid(axis='x', alpha=0.3)
                    ax.invert_yaxis()
                    
                    for i, v in enumerate(theme_values):
                        ax.text(v + max(theme_values)*0.02, i, str(v), 
                               va='center', fontweight='bold', fontsize=9)
                    
                    plt.tight_layout()
                    self._save_plot('federal_themes_analysis.png')
        
        return self.federal_children_df
    
    def compare_state_federal(self):
        """Compare state vs federal legislative approaches"""
        if self.federal_children_df is None or len(self.federal_children_df) == 0:
            print("\nInsufficient federal data for comparison")
            return None
        
        print("\n" + "="*80)
        print("STATE VS FEDERAL COMPARISON")
        print("="*80)
        
        # Count comparison
        state_total = len(self.children_related_df)
        fed_total = len(self.federal_children_df)
        
        print(f"\nBill Count:")
        print(f"  State bills:   {state_total}")
        print(f"  Federal bills: {fed_total}")
        print(f"  Ratio:         {state_total/fed_total:.1f}:1 (state:federal)")
        
        # Passed bills comparison
        state_passed = len(self.children_related_df[self.children_related_df['Status'] == 'Passed'])
        if 'Status' in self.federal_children_df.columns:
            fed_passed = len(self.federal_children_df[self.federal_children_df['Status'] == 'Passed'])
            print(f"\nPassed Bills:")
            print(f"  State passed:   {state_passed}")
            print(f"  Federal passed: {fed_passed}")
        
        # Visualization - ENHANCED with more charts
        
        # Chart 1: Volume and pass rate comparison
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Volume comparison
        ax1 = axes[0]
        categories = ['State', 'Federal']
        totals = [state_total, fed_total]
        colors = ['#3498db', '#e74c3c']
        bars1 = ax1.bar(categories, totals, color=colors, edgecolor='black', width=0.6, alpha=0.8)
        ax1.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax1.set_title('State vs Federal Bill Volume\n(Children\'s Online Safety)', fontweight='bold', fontsize=14)
        ax1.grid(axis='y', alpha=0.3)
        for i, v in enumerate(totals):
            ax1.text(i, v + max(totals)*0.02, str(v), ha='center', fontweight='bold', fontsize=12)
        
        # Pass rate comparison (if data available)
        ax2 = axes[1]
        if 'Status' in self.federal_children_df.columns:
            pass_rates = [
                (state_passed / state_total * 100),
                (fed_passed / fed_total * 100) if fed_total > 0 else 0
            ]
            bars2 = ax2.bar(categories, pass_rates, color=colors, edgecolor='black', width=0.6, alpha=0.8)
            ax2.set_ylabel('Pass Rate (%)', fontweight='bold', fontsize=12)
            ax2.set_title('State vs Federal Legislative Success Rate', fontweight='bold', fontsize=14)
            ax2.grid(axis='y', alpha=0.3)
            for i, v in enumerate(pass_rates):
                ax2.text(i, v + max(pass_rates)*0.02, f'{v:.1f}%', ha='center', fontweight='bold', fontsize=12)
        
        plt.tight_layout()
        self._save_plot('state_vs_federal_comparison.png')
        
        # NEW Chart 2: Detailed comparison radar chart style
        fig, ax = plt.subplots(figsize=(14, 8))
        
        metrics = []
        state_values = []
        federal_values = []
        
        # Total bills
        metrics.append('Total Bills\n(normalized)')
        state_values.append(min(state_total / 50, 100))  # Normalize to 0-100
        federal_values.append(min(fed_total / 50, 100))
        
        # Passed bills
        metrics.append('Passed Bills\n(normalized)')
        state_values.append(min(state_passed / 20, 100))
        if 'Status' in self.federal_children_df.columns:
            federal_values.append(min(fed_passed / 20, 100))
        else:
            federal_values.append(0)
        
        # Success rate
        metrics.append('Success Rate')
        state_values.append(state_passed / state_total * 100 if state_total > 0 else 0)
        if 'Status' in self.federal_children_df.columns and fed_total > 0:
            federal_values.append(fed_passed / fed_total * 100)
        else:
            federal_values.append(0)
        
        # Activity diversity (unique themes)
        if 'Themes' in self.children_related_df.columns:
            state_themes_unique = len(set([t.strip() for themes in self.children_related_df['Themes'].dropna() 
                                          for t in str(themes).split(',')]))
            metrics.append('Theme Diversity\n(unique themes)')
            state_values.append(min(state_themes_unique / 2, 100))
            
            if 'Themes' in self.federal_children_df.columns:
                fed_themes_unique = len(set([t.strip() for themes in self.federal_children_df['Themes'].dropna()
                                            for t in str(themes).split(',')]))
                federal_values.append(min(fed_themes_unique / 2, 100))
            else:
                federal_values.append(0)
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, state_values, width, label='State Legislation', 
                      color='#3498db', edgecolor='black', alpha=0.8)
        bars2 = ax.bar(x + width/2, federal_values, width, label='Federal Legislation',
                      color='#e74c3c', edgecolor='black', alpha=0.8)
        
        ax.set_ylabel('Score / Percentage', fontweight='bold', fontsize=12)
        ax.set_title('Comprehensive State vs Federal Comparison\n(Multiple Metrics)', 
                    fontweight='bold', fontsize=14)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, fontsize=10, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                       f'{height:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        self._save_plot('state_vs_federal_detailed_comparison.png')
        
        # NEW Chart 3: Timeline comparison (if both have dates)
        if 'Intro Date' in self.children_related_df.columns and 'Intro Date' in self.federal_children_df.columns:
            fig, ax = plt.subplots(figsize=(14, 6))
            
            # State timeline
            self.children_related_df['Year'] = pd.to_datetime(
                self.children_related_df['Intro Date'], format='%d/%m/%Y', errors='coerce'
            ).dt.year
            state_yearly = self.children_related_df.groupby('Year').size()
            
            # Federal timeline
            self.federal_children_df['Year'] = pd.to_datetime(
                self.federal_children_df['Intro Date'], format='%d/%m/%Y', errors='coerce'
            ).dt.year
            fed_yearly = self.federal_children_df.groupby('Year').size()
            
            # Plot both
            all_years = sorted(set(list(state_yearly.index) + list(fed_yearly.index)))
            state_values_timeline = [state_yearly.get(y, 0) for y in all_years]
            fed_values_timeline = [fed_yearly.get(y, 0) for y in all_years]
            
            ax.plot(all_years, state_values_timeline, marker='o', linewidth=3, markersize=10,
                   label='State Bills', color='#3498db', markeredgecolor='black', markeredgewidth=2)
            ax.plot(all_years, fed_values_timeline, marker='s', linewidth=3, markersize=10,
                   label='Federal Bills', color='#e74c3c', markeredgecolor='black', markeredgewidth=2)
            
            ax.fill_between(all_years, state_values_timeline, alpha=0.3, color='#3498db')
            ax.fill_between(all_years, fed_values_timeline, alpha=0.3, color='#e74c3c')
            
            ax.set_xlabel('Year', fontweight='bold', fontsize=12)
            ax.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
            ax.set_title('State vs Federal Legislative Activity Over Time', fontweight='bold', fontsize=14)
            ax.legend(fontsize=11, loc='best')
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            self._save_plot('state_vs_federal_timeline.png')
        
        print(f"\n✅ Comparison visualizations saved")
    
    # ========================================================================
    # PART 4: CHALLENGE-FOCUSED ANALYSIS (FEDERAL POLICY DEVELOPMENT)
    # ========================================================================
    
    def analyze_holistic_patterns(self):
        """Q1: How can state legislation provide holistic insights?"""
        if self.children_related_df is None:
            self.identify_children_related_bills()
        
        passed_df = self.children_related_df[self.children_related_df['Status'] == 'Passed']
        
        print("\n" + "="*80)
        print("Q1: HOLISTIC SOLUTION INSIGHTS FROM STATE LEGISLATION")
        print("="*80)
        
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
        
        state_scores = {}
        for state in passed_df['State'].unique():
            state_bills = passed_df[passed_df['State'] == state]
            scores = {}
            
            for dimension, keywords in dimensions.items():
                count = 0
                for _, bill in state_bills.iterrows():
                    text = f"{bill['Name']} {bill['Description']} {bill['Themes']}"
                    if any(kw.lower() in text.lower() for kw in keywords):
                        count += 1
                scores[dimension] = count
            
            state_scores[state] = scores
        
        state_df = pd.DataFrame(state_scores).T
        state_df['Total_Dimensions'] = (state_df > 0).sum(axis=1)
        state_df['Total_Bills'] = [len(passed_df[passed_df['State'] == s]) for s in state_df.index]
        
        comprehensive_states = state_df.nlargest(10, 'Total_Dimensions')
        
        print("\nTop 10 Most Comprehensive State Approaches:")
        print(f"{'State':<20} {'Dimensions':<12} {'Bills':<10} {'Key Strengths'}")
        print("-" * 80)
        for state, row in comprehensive_states.iterrows():
            dims = row['Total_Dimensions']
            bills = row['Total_Bills']
            strengths = state_df.loc[state].nlargest(3).index.tolist()
            print(f"{state:<20} {dims:<12} {bills:<10} {', '.join(strengths[:2])}")
        
        # Visualizations - ENHANCED
        
        # Chart 1: Heatmap
        plt.figure(figsize=(14, 10))
        top_states = state_df.nlargest(20, 'Total_Bills')
        heatmap_data = top_states[list(dimensions.keys())]
        sns.heatmap(heatmap_data, annot=True, fmt='g', cmap='YlOrRd', 
                   cbar_kws={'label': 'Number of Bills'}, linewidths=0.5, linecolor='gray')
        plt.title('Multi-Dimensional Approach by State\n(Comprehensive vs Single-Issue Legislation)', 
                 fontsize=14, fontweight='bold', pad=20)
        plt.xlabel('Policy Dimension', fontweight='bold')
        plt.ylabel('State', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        self._save_plot('challenge_holistic_heatmap.png')
        
        # NEW Chart 2: Dimension coverage distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Distribution of how many dimensions states cover
        dimension_dist = state_df['Total_Dimensions'].value_counts().sort_index()
        colors_dist = plt.cm.viridis(np.linspace(0.3, 0.9, len(dimension_dist)))
        bars = ax1.bar(dimension_dist.index, dimension_dist.values, color=colors_dist, 
                      edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Number of Dimensions Covered', fontweight='bold', fontsize=12)
        ax1.set_ylabel('Number of States', fontweight='bold', fontsize=12)
        ax1.set_title('Distribution of State Approach Comprehensiveness', fontweight='bold', fontsize=14)
        ax1.grid(axis='y', alpha=0.3)
        for i, (dim, count) in enumerate(dimension_dist.items()):
            ax1.text(dim, count + max(dimension_dist.values)*0.02, str(count), 
                    ha='center', fontweight='bold')
        
        # Most/least covered dimensions
        dimension_totals = state_df[list(dimensions.keys())].sum().sort_values(ascending=False)
        colors_dim = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(dimension_totals)))
        ax2.barh(dimension_totals.index, dimension_totals.values, color=colors_dim, 
                edgecolor='black', alpha=0.8)
        ax2.set_xlabel('Total Bills Across All States', fontweight='bold', fontsize=12)
        ax2.set_title('Policy Dimension Popularity', fontweight='bold', fontsize=14)
        ax2.grid(axis='x', alpha=0.3)
        ax2.invert_yaxis()
        for i, v in enumerate(dimension_totals.values):
            ax2.text(v + max(dimension_totals.values)*0.02, i, str(int(v)), 
                    va='center', fontweight='bold')
        
        plt.tight_layout()
        self._save_plot('challenge_holistic_dimensions_analysis.png')
        
        # NEW Chart 3: Top comprehensive states radar-style comparison
        fig, ax = plt.subplots(figsize=(14, 8))
        top_5_comp = comprehensive_states.head(5)
        
        x = np.arange(len(dimensions))
        width = 0.15
        
        colors_comp = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
        for i, (state, row) in enumerate(top_5_comp.iterrows()):
            values = [row[dim] for dim in dimensions.keys()]
            ax.bar(x + i*width, values, width, label=state, color=colors_comp[i], 
                  edgecolor='black', alpha=0.8)
        
        ax.set_xlabel('Policy Dimension', fontweight='bold', fontsize=12)
        ax.set_ylabel('Number of Bills', fontweight='bold', fontsize=12)
        ax.set_title('Top 5 Most Comprehensive States\n(Bill Count by Dimension)', 
                    fontweight='bold', fontsize=14)
        ax.set_xticks(x + width * 2)
        ax.set_xticklabels(dimensions.keys(), rotation=45, ha='right')
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        self._save_plot('challenge_holistic_top_states_comparison.png')
        
        self._save_csv(state_df, 'challenge_holistic_state_scores.csv')
        
        return state_df, dimensions
    
    def analyze_state_consensus(self):
        """Q2: Where do states agree or disagree?"""
        if self.children_related_df is None:
            self.identify_children_related_bills()
        
        passed_df = self.children_related_df[self.children_related_df['Status'] == 'Passed']
        
        print("\n" + "="*80)
        print("Q2: STATE CONSENSUS AND DIVERGENCE ANALYSIS")
        print("="*80)
        
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
            'Mental Health': ['mental health', 'wellness', 'psychological']
        }
        
        provision_adoption = {}
        state_provisions = {}
        
        for state in passed_df['State'].unique():
            state_bills = passed_df[passed_df['State'] == state]
            state_text = ' '.join(state_bills['Name'].fillna('') + ' ' + 
                                 state_bills['Description'].fillna('')).lower()
            state_provisions[state] = []
            
            for provision, keywords in provisions.items():
                if any(kw in state_text for kw in keywords):
                    provision_adoption[provision] = provision_adoption.get(provision, 0) + 1
                    state_provisions[state].append(provision)
        
        total_states = len(passed_df['State'].unique())
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
        
        # Visualizations - ENHANCED
        
        # Chart 1: Consensus spectrum
        fig, ax = plt.subplots(figsize=(14, 9))
        colors = provision_df['Category'].map({
            'Universal': '#2ecc71',
            'High Consensus': '#3498db',
            'Moderate Adoption': '#f39c12',
            'Divergent': '#e74c3c'
        })
        bars = ax.barh(provision_df['Provision'], provision_df['Percentage'], color=colors, 
                      edgecolor='black', alpha=0.8)
        ax.axvline(x=75, color='green', linestyle='--', alpha=0.7, linewidth=2, label='Universal (75%+)')
        ax.axvline(x=50, color='blue', linestyle='--', alpha=0.7, linewidth=2, label='High Consensus (50%+)')
        ax.axvline(x=25, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='Moderate (25%+)')
        ax.set_xlabel('% of States Adopting', fontsize=12, fontweight='bold')
        ax.set_title('State Consensus on Policy Provisions\n(Adoption Rate Spectrum)', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10, loc='lower right')
        ax.grid(axis='x', alpha=0.3)
        
        # Add percentage labels
        for i, (idx, row) in enumerate(provision_df.iterrows()):
            ax.text(row['Percentage'] + 2, i, f"{row['Percentage']:.1f}% ({row['States']} states)", 
                   va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        self._save_plot('challenge_consensus_analysis.png')
        
        # NEW Chart 2: Consensus categories pie chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Category distribution
        category_counts = provision_df['Category'].value_counts()
        colors_cat = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
        ax1.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
               startangle=90, colors=colors_cat, textprops={'fontweight': 'bold', 'fontsize': 11})
        ax1.set_title('Distribution of Provisions by Consensus Level', fontweight='bold', fontsize=14)
        
        # Average adoption by category
        avg_by_category = provision_df.groupby('Category')['Percentage'].mean().sort_values(ascending=False)
        colors_avg = [colors_cat[['Universal', 'High Consensus', 'Moderate Adoption', 'Divergent'].index(cat)] 
                     for cat in avg_by_category.index]
        bars = ax2.bar(range(len(avg_by_category)), avg_by_category.values, 
                      color=colors_avg, edgecolor='black', alpha=0.8)
        ax2.set_xticks(range(len(avg_by_category)))
        ax2.set_xticklabels(avg_by_category.index, rotation=45, ha='right')
        ax2.set_ylabel('Average Adoption Rate (%)', fontweight='bold', fontsize=12)
        ax2.set_title('Average Adoption by Consensus Category', fontweight='bold', fontsize=14)
        ax2.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(avg_by_category.values):
            ax2.text(i, v + max(avg_by_category.values)*0.02, f'{v:.1f}%', 
                    ha='center', fontweight='bold')
        
        plt.tight_layout()
        self._save_plot('challenge_consensus_categories.png')
        
        # NEW Chart 3: Provision co-occurrence network visualization
        fig, ax = plt.subplots(figsize=(12, 12))
        
        # Calculate co-occurrence matrix
        co_occurrence = np.zeros((len(provisions), len(provisions)))
        prov_list = list(provisions.keys())
        
        for state_provs in state_provisions.values():
            for i, prov1 in enumerate(prov_list):
                for j, prov2 in enumerate(prov_list):
                    if prov1 in state_provs and prov2 in state_provs and i != j:
                        co_occurrence[i][j] += 1
        
        # Create heatmap
        sns.heatmap(co_occurrence, annot=True, fmt='.0f', cmap='Blues',
                   xticklabels=prov_list, yticklabels=prov_list,
                   cbar_kws={'label': 'States with Both Provisions'},
                   linewidths=0.5, linecolor='gray')
        plt.title('Provision Co-Adoption Network\n(How often provisions appear together)', 
                 fontweight='bold', fontsize=14, pad=20)
        plt.xlabel('Provision', fontweight='bold')
        plt.ylabel('Provision', fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        self._save_plot('challenge_consensus_cooccurrence.png')
        
        self._save_csv(provision_df, 'challenge_provision_consensus.csv')
        
        return provision_df, state_provisions
    
    def analyze_federalism_balance(self):
        """Q3: What should be kept at state level?"""
        if self.children_related_df is None:
            self.identify_children_related_bills()
        
        passed_df = self.children_related_df[self.children_related_df['Status'] == 'Passed']
        
        print("\n" + "="*80)
        print("Q3: FEDERAL VS STATE JURISDICTION ANALYSIS")
        print("="*80)
        
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
        
        provisions_analysis = []
        
        for provision, keywords in provisions.items():
            state_count = 0
            for state in passed_df['State'].unique():
                state_bills = passed_df[passed_df['State'] == state]
                state_text = ' '.join(state_bills['Description'].fillna('')).lower()
                if any(kw in state_text for kw in keywords):
                    state_count += 1
            
            adoption_rate = (state_count / passed_df['State'].nunique()) * 100
            
            if adoption_rate >= 75:
                if provision in ['Age Verification', 'Data Privacy', 'Platform Liability']:
                    category = 'Strong Federal Candidates'
                else:
                    category = 'Federal Framework with State Flexibility'
            elif adoption_rate >= 25:
                category = 'Federal Framework with State Flexibility'
            else:
                category = 'Best Left to States'
            
            provisions_analysis.append({
                'Provision': provision,
                'Adoption_Rate': adoption_rate,
                'States': state_count,
                'Recommendation': category
            })
        
        prov_df = pd.DataFrame(provisions_analysis)
        
        print(f"\n{'Provision':<30} {'Adoption %':<12} {'Recommendation'}")
        print("-"*80)
        for _, row in prov_df.iterrows():
            print(f"{row['Provision']:<30} {row['Adoption_Rate']:<12.1f} {row['Recommendation']}")
        
        # Visualizations - ENHANCED
        
        # Chart 1: Main jurisdiction recommendation chart
        fig, ax = plt.subplots(figsize=(14, 9))
        prov_sorted = prov_df.sort_values('Adoption_Rate', ascending=True)
        colors_map = {
            'Strong Federal Candidates': '#27ae60',
            'Federal Framework with State Flexibility': '#3498db',
            'Best Left to States': '#e67e22'
        }
        colors = [colors_map[rec] for rec in prov_sorted['Recommendation']]
        bars = ax.barh(prov_sorted['Provision'], prov_sorted['Adoption_Rate'], 
                      color=colors, edgecolor='black', alpha=0.8)
        ax.axvline(x=75, color='green', linestyle='--', alpha=0.7, linewidth=2, label='Federal threshold (75%)')
        ax.axvline(x=25, color='orange', linestyle='--', alpha=0.7, linewidth=2, label='State threshold (25%)')
        ax.set_xlabel('State Adoption Rate (%)', fontsize=12, fontweight='bold')
        ax.set_title('Federal vs State Jurisdiction Recommendations\n(Based on State Adoption Patterns)', 
                    fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        
        # Add labels
        for i, (idx, row) in enumerate(prov_sorted.iterrows()):
            ax.text(row['Adoption_Rate'] + 2, i, f"{row['Adoption_Rate']:.1f}%", 
                   va='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        self._save_plot('challenge_federalism_analysis.png')
        
        # NEW Chart 2: Recommendation distribution
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Pie chart of recommendations
        rec_counts = prov_df['Recommendation'].value_counts()
        colors_rec = [colors_map[rec] for rec in rec_counts.index]
        wedges, texts, autotexts = ax1.pie(rec_counts.values, labels=rec_counts.index, 
                                           autopct='%1.1f%%', startangle=90, colors=colors_rec,
                                           textprops={'fontweight': 'bold', 'fontsize': 10})
        ax1.set_title('Distribution of Jurisdiction Recommendations', fontweight='bold', fontsize=14)
        
        # Average adoption rate by recommendation
        avg_by_rec = prov_df.groupby('Recommendation')['Adoption_Rate'].mean().sort_values(ascending=False)
        colors_avg_rec = [colors_map[rec] for rec in avg_by_rec.index]
        bars = ax2.bar(range(len(avg_by_rec)), avg_by_rec.values, 
                      color=colors_avg_rec, edgecolor='black', alpha=0.8, width=0.6)
        ax2.set_xticks(range(len(avg_by_rec)))
        ax2.set_xticklabels(avg_by_rec.index, rotation=15, ha='right', fontsize=9)
        ax2.set_ylabel('Average Adoption Rate (%)', fontweight='bold', fontsize=12)
        ax2.set_title('Average State Adoption by Jurisdiction Type', fontweight='bold', fontsize=14)
        ax2.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(avg_by_rec.values):
            ax2.text(i, v + max(avg_by_rec.values)*0.02, f'{v:.1f}%', 
                    ha='center', fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        self._save_plot('challenge_federalism_distribution.png')
        
        self._save_csv(prov_df, 'challenge_federalism_recommendations.csv')
        
        return prov_df
    
    def analyze_privacy_effectiveness(self):
        """Q4: What approaches ensure privacy + effectiveness?"""
        if self.children_related_df is None:
            self.identify_children_related_bills()
        
        passed_df = self.children_related_df[self.children_related_df['Status'] == 'Passed']
        
        print("\n" + "="*80)
        print("Q4: PRIVACY + EFFECTIVENESS ANALYSIS")
        print("="*80)
        
        # Age verification methods
        age_methods = {
            'Government ID': ['government id', 'driver license', 'state id'],
            'Third-Party Verification': ['third party', 'third-party', 'verification service'],
            'Age Estimation': ['age estimation', 'age assurance', 'facial analysis'],
            'Parental Consent': ['parental consent', 'parent approval'],
            'Privacy-Preserving': ['privacy preserving', 'privacy-preserving', 'anonymous verification']
        }
        
        method_adoption = {}
        for method, keywords in age_methods.items():
            states_using = []
            for state in passed_df['State'].unique():
                state_bills = passed_df[passed_df['State'] == state]
                state_text = ' '.join(state_bills['Description'].fillna('')).lower()
                if any(kw in state_text for kw in keywords):
                    states_using.append(state)
            method_adoption[method] = len(states_using)
        
        print("\nAge Verification Methods (States Using):")
        print(f"{'Method':<30} {'States'}")
        print("-"*50)
        for method, count in sorted(method_adoption.items(), key=lambda x: x[1], reverse=True):
            print(f"{method:<30} {count}")
        
        # Data protection practices
        data_practices = {
            'Data Deletion Required': ['delete', 'deletion', 'remove data'],
            'Minimal Collection': ['minimal', 'minimum', 'necessary data'],
            'No Retention of ID': ['not retain', 'no retention'],
            'Anonymization': ['anonymize', 'anonymous', 'de-identify'],
            'Purpose Limitation': ['purpose limitation', 'specified purpose']
        }
        
        practice_counts = {}
        for practice, keywords in data_practices.items():
            count = sum(1 for _, bill in passed_df.iterrows() 
                       if any(kw in str(bill['Description']).lower() for kw in keywords))
            practice_counts[practice] = count
        
        print(f"\n\nData Protection Practices:")
        print(f"{'Practice':<35} {'Bills'}")
        print("-"*50)
        for practice, count in sorted(practice_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"{practice:<35} {count}")
        
        # Save data
        method_df = pd.DataFrame(list(method_adoption.items()), 
                                columns=['Method', 'States'])
        self._save_csv(method_df, 'challenge_age_verification_methods.csv')
        
        practice_df = pd.DataFrame(list(practice_counts.items()),
                                  columns=['Practice', 'Bills'])
        self._save_csv(practice_df, 'challenge_data_protection_practices.csv')
        
        # Visualizations - ENHANCED
        
        # Chart 1: Age verification and data protection (original enhanced)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        method_df_sorted = method_df.sort_values('States')
        colors_method = plt.cm.Blues(np.linspace(0.4, 0.9, len(method_df_sorted)))
        bars1 = ax1.barh(method_df_sorted['Method'], method_df_sorted['States'], 
                        color=colors_method, edgecolor='black', alpha=0.8)
        ax1.set_xlabel('Number of States', fontsize=12, fontweight='bold')
        ax1.set_title('Age Verification Methods Adoption\n(State-Level Implementation)', 
                     fontsize=14, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        for i, v in enumerate(method_df_sorted['States'].values):
            ax1.text(v + max(method_df_sorted['States'])*0.02, i, str(v), 
                    va='center', fontweight='bold', fontsize=10)
        
        practice_df_sorted = practice_df.sort_values('Bills')
        colors_practice = plt.cm.Greens(np.linspace(0.4, 0.9, len(practice_df_sorted)))
        bars2 = ax2.barh(practice_df_sorted['Practice'], practice_df_sorted['Bills'],
                        color=colors_practice, edgecolor='black', alpha=0.8)
        ax2.set_xlabel('Number of Bills', fontsize=12, fontweight='bold')
        ax2.set_title('Data Protection Practices in Legislation', fontsize=14, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        for i, v in enumerate(practice_df_sorted['Bills'].values):
            ax2.text(v + max(practice_df_sorted['Bills'])*0.02, i, str(v), 
                    va='center', fontweight='bold', fontsize=10)
        
        plt.tight_layout()
        self._save_plot('challenge_privacy_effectiveness.png')
        
        # NEW Chart 2: Privacy vs Effectiveness Matrix
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Assign privacy and effectiveness scores to methods
        privacy_scores = {
            'Privacy-Preserving': 95,
            'Third-Party Verification': 70,
            'Age Estimation': 60,
            'Parental Consent': 80,
            'Government ID': 40
        }
        
        effectiveness_scores = {
            'Privacy-Preserving': 75,
            'Third-Party Verification': 90,
            'Age Estimation': 60,
            'Parental Consent': 70,
            'Government ID': 95
        }
        
        methods = list(method_adoption.keys())
        privacy_vals = [privacy_scores.get(m, 50) for m in methods]
        effectiveness_vals = [effectiveness_scores.get(m, 50) for m in methods]
        sizes = [method_adoption[m] * 100 for m in methods]
        
        scatter = ax.scatter(privacy_vals, effectiveness_vals, s=sizes, alpha=0.6,
                           c=sizes, cmap='RdYlGn', edgecolors='black', linewidth=2)
        
        # Add method labels
        for i, method in enumerate(methods):
            ax.annotate(f"{method}\n({method_adoption[method]} states)", 
                       (privacy_vals[i], effectiveness_vals[i]),
                       fontsize=9, fontweight='bold', ha='center', alpha=0.8)
        
        ax.set_xlabel('Privacy Protection Score', fontweight='bold', fontsize=12)
        ax.set_ylabel('Effectiveness Score', fontweight='bold', fontsize=12)
        ax.set_title('Age Verification: Privacy vs Effectiveness Trade-offs\n(Bubble size = State adoption)', 
                    fontweight='bold', fontsize=14)
        ax.grid(True, alpha=0.3)
        ax.set_xlim(30, 100)
        ax.set_ylim(50, 100)
        
        # Add quadrant lines
        ax.axhline(y=75, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(x=65, color='gray', linestyle='--', alpha=0.5)
        
        # Add quadrant labels
        ax.text(95, 95, 'Ideal Zone', ha='right', va='top', 
               fontsize=11, style='italic', alpha=0.5, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
        
        plt.tight_layout()
        self._save_plot('challenge_privacy_effectiveness_matrix.png')
        
        # NEW Chart 3: Combined privacy & effectiveness score
        fig, ax = plt.subplots(figsize=(14, 8))
        
        combined_data = []
        for method in methods:
            if method in method_adoption:
                combined_score = (privacy_scores.get(method, 50) + effectiveness_scores.get(method, 50)) / 2
                combined_data.append({
                    'Method': method,
                    'Privacy': privacy_scores.get(method, 50),
                    'Effectiveness': effectiveness_scores.get(method, 50),
                    'Combined': combined_score,
                    'Adoption': method_adoption[method]
                })
        
        combined_df = pd.DataFrame(combined_data).sort_values('Combined', ascending=True)
        
        x = np.arange(len(combined_df))
        width = 0.35
        
        bars1 = ax.barh(x - width/2, combined_df['Privacy'], width, 
                       label='Privacy Score', color='#3498db', edgecolor='black', alpha=0.8)
        bars2 = ax.barh(x + width/2, combined_df['Effectiveness'], width,
                       label='Effectiveness Score', color='#e74c3c', edgecolor='black', alpha=0.8)
        
        ax.set_yticks(x)
        ax.set_yticklabels([f"{row['Method']} ({row['Adoption']} states)" 
                           for _, row in combined_df.iterrows()], fontsize=10)
        ax.set_xlabel('Score (0-100)', fontweight='bold', fontsize=12)
        ax.set_title('Age Verification Methods: Privacy & Effectiveness Comparison\n(With State Adoption)', 
                    fontweight='bold', fontsize=14)
        ax.legend(fontsize=11)
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        self._save_plot('challenge_privacy_effectiveness_comparison.png')
        
        # NEW Chart 4: Data protection practices ranking
        fig, ax = plt.subplots(figsize=(12, 8))
        
        practice_sorted = practice_df.sort_values('Bills', ascending=False)
        total_passed = len(passed_df)
        percentages = (practice_sorted['Bills'] / total_passed * 100).values
        
        colors_prac = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(practice_sorted)))
        bars = ax.bar(range(len(practice_sorted)), percentages, 
                     color=colors_prac, edgecolor='black', alpha=0.8)
        
        ax.set_xticks(range(len(practice_sorted)))
        ax.set_xticklabels(practice_sorted['Practice'], rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('% of Passed Bills', fontweight='bold', fontsize=12)
        ax.set_title('Data Protection Practices: Adoption Rate in Passed Legislation', 
                    fontweight='bold', fontsize=14)
        ax.grid(axis='y', alpha=0.3)
        
        for i, (pct, count) in enumerate(zip(percentages, practice_sorted['Bills'].values)):
            ax.text(i, pct + max(percentages)*0.02, f'{pct:.1f}%\n({count} bills)', 
                   ha='center', fontweight='bold', fontsize=9)
        
        plt.tight_layout()
        self._save_plot('challenge_data_protection_ranking.png')
        
        return method_adoption, practice_counts
    
    # ========================================================================
    # PART 5: COMPREHENSIVE REPORTING
    # ========================================================================
    
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
        
        # Save to file
        rec_path = os.path.join(self.output_dir, 'FEDERAL_RECOMMENDATIONS.md')
        with open(rec_path, 'w', encoding='utf-8') as f:
            f.write("# Federal Policy Recommendations\n")
            f.write("## Based on Comprehensive State Legislative Analysis\n\n")
            for category, items in recommendations.items():
                f.write(f"\n### {category}\n\n")
                for item in items:
                    f.write(f"- {item}\n")
        
        print(f"\n📄 Recommendations saved to: {rec_path}")
        
        return recommendations
    
    def generate_comprehensive_report(self):
        """Generate the comprehensive analysis report"""
        print("\n" + "="*80)
        print("COMPREHENSIVE CHILDREN'S ONLINE SAFETY POLICY ANALYSIS")
        print("State & Federal Legislative Landscape")
        print("="*80)
        
        start_time = time.time()
        
        # Part 1: Identify bills
        print("\n[1/9] Identifying children-related bills...")
        self.identify_children_related_bills()
        
        # Part 2: State analysis
        print("\n[2/9] Analyzing state legislation...")
        status_counts, state_summary, theme_counts = self.analyze_state_bills()
        
        # Part 3: Federal analysis
        print("\n[3/9] Analyzing federal legislation...")
        self.analyze_federal_bills()
        
        # Part 4: State-Federal comparison
        print("\n[4/9] Comparing state and federal approaches...")
        self.compare_state_federal()
        
        # Part 5-8: Challenge questions
        print("\n[5/9] Analyzing holistic patterns (Challenge Q1)...")
        self.analyze_holistic_patterns()
        
        print("\n[6/9] Analyzing state consensus (Challenge Q2)...")
        self.analyze_state_consensus()
        
        print("\n[7/9] Analyzing federalism balance (Challenge Q3)...")
        self.analyze_federalism_balance()
        
        print("\n[8/9] Analyzing privacy & effectiveness (Challenge Q4)...")
        self.analyze_privacy_effectiveness()
        
        # Part 9: Federal recommendations
        print("\n[9/9] Generating federal policy recommendations...")
        self.generate_federal_recommendations()
        
        # Summary
        elapsed = time.time() - start_time
        self.stats['processing_time']['total_analysis'] = elapsed
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"\n⏱️  Total analysis time: {elapsed:.2f} seconds")
        print(f"\n📊 Results saved to: {self.output_dir}")
        
        # List generated files
        print("\n📁 Generated Files:")
        print("\n  State Analysis:")
        print("    - state_status_distribution.png")
        print("    - state_top_states.png")
        print("    - state_themes_wordcloud.png")
        print("    - state_status_analysis.csv")
        print("    - state_by_state_analysis.csv")
        
        if self.federal_df is not None:
            print("\n  Federal Analysis:")
            print("    - federal_status_distribution.png")
            print("    - federal_status_analysis.csv")
            print("    - state_vs_federal_comparison.png")
        
        print("\n  Challenge Analysis:")
        print("    - challenge_holistic_heatmap.png")
        print("    - challenge_consensus_analysis.png")
        print("    - challenge_federalism_analysis.png")
        print("    - challenge_privacy_effectiveness.png")
        print("    - challenge_holistic_state_scores.csv")
        print("    - challenge_provision_consensus.csv")
        print("    - challenge_federalism_recommendations.csv")
        print("    - challenge_age_verification_methods.csv")
        print("    - challenge_data_protection_practices.csv")
        
        print("\n  Policy Recommendations:")
        print("    - FEDERAL_RECOMMENDATIONS.md")
        
        print("\n✅ Comprehensive analysis complete!")
        
        # Generate summary statistics
        summary = {
            'Total State Bills Analyzed': len(self.state_df),
            'Children-Related State Bills': len(self.children_related_df),
            'State Bills Passed': len(self.children_related_df[self.children_related_df['Status'] == 'Passed']),
            'States with Passed Legislation': self.children_related_df[self.children_related_df['Status'] == 'Passed']['State'].nunique(),
            'Total Federal Bills Analyzed': len(self.federal_df) if self.federal_df is not None else 0,
            'Children-Related Federal Bills': len(self.federal_children_df) if self.federal_children_df is not None else 0,
            'Analysis Duration (seconds)': elapsed
        }
        
        summary_df = pd.DataFrame([summary])
        self._save_csv(summary_df, 'COMPREHENSIVE_SUMMARY.csv')
        
        return summary


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Comprehensive analysis of children\'s online safety legislation (State & Federal)',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--states', nargs='+', metavar='STATE',
                       help='Filter to specific states')
    parser.add_argument('--start-date', metavar='DATE',
                       help='Start date for filtering (YYYY-MM-DD)')
    parser.add_argument('--end-date', metavar='DATE',
                       help='End date for filtering (YYYY-MM-DD)')
    parser.add_argument('--output-dir', metavar='DIR',
                       help='Custom output directory')
    parser.add_argument('--quiet', action='store_true',
                       help='Minimal console output')
    
    args = parser.parse_args()
    
    # Parse date range
    date_range = None
    if args.start_date and args.end_date:
        try:
            start = pd.to_datetime(args.start_date)
            end = pd.to_datetime(args.end_date)
            date_range = (start, end)
        except Exception as e:
            logging.error(f"Invalid date format: {e}")
            return
    
    # File paths
    state_csv = "Technology Policy Tracking - Updated - US State.csv"
    federal_csv = "Technology Policy Tracking - Updated - US Federal.csv"
    
    if not os.path.exists(state_csv):
        print(f"Error: Cannot find '{state_csv}' in current directory")
        return
    
    # Initialize analyzer
    try:
        analyzer = ComprehensivePolicyAnalyzer(
            state_csv,
            federal_csv if os.path.exists(federal_csv) else None,
            output_dir=args.output_dir,
            states_filter=args.states,
            date_range=date_range,
            verbose=not args.quiet
        )
    except Exception as e:
        logging.error(f"Failed to initialize analyzer: {e}")
        print(f"Error: {e}")
        return
    
    # Run comprehensive analysis
    try:
        analyzer.generate_comprehensive_report()
    except Exception as e:
        logging.error(f"Analysis failed: {e}", exc_info=True)
        print(f"\nError during analysis: {e}")
        return


if __name__ == "__main__":
    main()
