#!/usr/bin/env python3
"""
populate.py - Dataset Population Script for Enhanced RAG System
Fixed version that handles Unicode issues and deprecation warnings
"""

import os
import requests
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any
import warnings
from datetime import datetime, timedelta

# Handle fpdf import properly
try:
    from fpdf import FPDF
    from fpdf.enums import XPos, YPos
    FPDF_AVAILABLE = True
except ImportError:
    print("⚠️ fpdf2 not available. Install with: pip install fpdf2")
    FPDF_AVAILABLE = False

# Try to import other packages with fallbacks
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    DATA_VIZ_AVAILABLE = True
except ImportError:
    print("⚠️ Data visualization packages not available.")
    DATA_VIZ_AVAILABLE = False

try:
    import arxiv
    ARXIV_AVAILABLE = True
except ImportError:
    print("⚠️ arxiv package not available.")
    ARXIV_AVAILABLE = False

# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class RAGDatasetPopulator:
    def __init__(self, output_dir: str = "rag_dataset"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "research_papers").mkdir(exist_ok=True)
        (self.output_dir / "business_reports").mkdir(exist_ok=True)
        (self.output_dir / "technical_docs").mkdir(exist_ok=True)
        (self.output_dir / "generated_docs").mkdir(exist_ok=True)
        
        print(f"📁 Dataset directory created: {self.output_dir}")

    def download_arxiv_papers(self, query: str = "retrieval augmented generation", max_papers: int = 3):
        """Download research papers from ArXiv"""
        if not ARXIV_AVAILABLE:
            print("⚠️ Skipping ArXiv download - arxiv package not available")
            return []
        
        print(f"📚 Downloading ArXiv papers for query: '{query}'")
        
        try:
            # Use the new Client API to avoid deprecation warning
            client = arxiv.Client()
            search = arxiv.Search(
                query=query,
                max_results=max_papers,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            papers_info = []
            for i, paper in enumerate(client.results(search)):
                try:
                    # Clean filename for Windows compatibility
                    safe_id = paper.entry_id.split('/')[-1].replace('v', '_v').replace(':', '_')
                    filename = f"arxiv_{safe_id}.pdf"
                    filepath = self.output_dir / "research_papers" / filename
                    
                    paper.download_pdf(dirpath=str(self.output_dir / "research_papers"), 
                                     filename=filename)
                    
                    papers_info.append({
                        'title': paper.title,
                        'authors': [str(author) for author in paper.authors],
                        'published': paper.published.isoformat(),
                        'summary': paper.summary,
                        'filename': filename,
                        'categories': paper.categories
                    })
                    
                    print(f"✅ Downloaded: {paper.title[:50]}...")
                    time.sleep(2)  # Rate limiting
                    
                except Exception as e:
                    print(f"⚠️ Error downloading {paper.title}: {e}")
                    continue
            
            # Save metadata
            with open(self.output_dir / "arxiv_papers_metadata.json", 'w') as f:
                json.dump(papers_info, f, indent=2)
            
            print(f"📄 Downloaded {len(papers_info)} ArXiv papers")
            return papers_info
            
        except Exception as e:
            print(f"❌ Error accessing ArXiv: {e}")
            return []

    def generate_synthetic_business_report(self, company_name: str, year: int = 2024) -> str:
        """Generate synthetic business report with data - Unicode safe"""
        if not FPDF_AVAILABLE:
            print(f"⚠️ Skipping {company_name} report - fpdf2 not available")
            return ""
        
        class BusinessPDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 15)
                self.cell(0, 10, f'{company_name} Annual Report {year}', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                self.ln(10)
            
            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', align='C')

        # Generate realistic business data
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        revenue_data = [random.uniform(50, 100) for _ in quarters]
        profit_data = [r * random.uniform(0.1, 0.3) for r in revenue_data]
        
        # Create visualizations if matplotlib available
        if DATA_VIZ_AVAILABLE:
            try:
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                
                # Revenue chart
                ax1.bar(quarters, revenue_data, color='skyblue')
                ax1.set_title(f'{company_name} Quarterly Revenue ({year})')
                ax1.set_ylabel('Revenue (millions $)')
                
                # Profit trend
                ax2.plot(quarters, profit_data, marker='o', color='green')
                ax2.set_title(f'{company_name} Quarterly Profit ({year})')
                ax2.set_ylabel('Profit (millions $)')
                
                plt.tight_layout()
                chart_path = self.output_dir / "generated_docs" / f"{company_name.replace(' ', '_')}_charts.png"
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
            except Exception as e:
                print(f"⚠️ Could not generate charts: {e}")
        
        # Create PDF report
        pdf = BusinessPDF()
        pdf.add_page()
        
        # Executive Summary
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Executive Summary', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        
        # Use plain text without Unicode characters
        summary_text = f"""
{company_name} delivered strong performance in {year} with total revenue of 
${sum(revenue_data):.1f} million, representing a growth of {random.uniform(5, 25):.1f}% 
year-over-year. The company's strategic initiatives in digital transformation 
and market expansion contributed to improved operational efficiency.

Key Financial Highlights:
- Total Revenue: ${sum(revenue_data):.1f} million
- Net Profit: ${sum(profit_data):.1f} million  
- Profit Margin: {(sum(profit_data)/sum(revenue_data)*100):.1f}%
- Return on Investment: {random.uniform(10, 20):.1f}%

Market Position:
The company maintained its market leadership position with a {random.uniform(15, 35):.1f}% 
market share in the industry. Customer satisfaction scores improved to {random.uniform(85, 95):.1f}%, 
reflecting our commitment to service excellence.

Operational Metrics:
- Employee Count: {random.randint(500, 5000)}
- Office Locations: {random.randint(5, 50)}
- Global Reach: {random.randint(10, 100)} countries
- Technology Investment: ${random.uniform(5, 25):.1f} million
        """
        
        # Add text to PDF
        pdf.multi_cell(0, 6, summary_text.strip())
        
        # Financial Performance Section
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Financial Performance Analysis', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        
        # Quarterly breakdown
        for i, quarter in enumerate(quarters):
            pdf.cell(0, 8, f'{quarter} {year}: Revenue ${revenue_data[i]:.1f}M, Profit ${profit_data[i]:.1f}M', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Statistical Analysis
        pdf.ln(5)
        if DATA_VIZ_AVAILABLE:
            mean_revenue = np.mean(revenue_data)
            std_revenue = np.std(revenue_data)
            growth_rate = ((revenue_data[3]-revenue_data[0])/revenue_data[0]*100)
        else:
            mean_revenue = sum(revenue_data) / len(revenue_data)
            std_revenue = (sum([(x - mean_revenue)**2 for x in revenue_data]) / len(revenue_data))**0.5
            growth_rate = ((revenue_data[3]-revenue_data[0])/revenue_data[0]*100)
        
        stats_text = f"""
Statistical Analysis:
- Average quarterly revenue: ${mean_revenue:.1f} million
- Revenue standard deviation: ${std_revenue:.1f} million
- Revenue growth rate Q4 vs Q1: {growth_rate:.1f}%
- Employee productivity: ${random.uniform(150, 300):.0f}K revenue per employee
- Customer acquisition cost: ${random.uniform(50, 200):.0f}
- Customer lifetime value: ${random.uniform(1000, 5000):.0f}

Industry Benchmarks:
- Market Share: {random.uniform(10, 40):.1f}%
- Industry Growth Rate: {random.uniform(3, 15):.1f}%
- Competitive Position: Top {random.randint(3, 10)}
- ESG Score: {random.uniform(70, 95):.1f}/100
        """
        
        pdf.multi_cell(0, 6, stats_text.strip())
        
        # Save PDF
        filename = f"{company_name.replace(' ', '_')}_annual_report_{year}.pdf"
        filepath = self.output_dir / "business_reports" / filename
        pdf.output(str(filepath))
        
        return str(filepath)

    def generate_technical_documentation(self, product_name: str) -> str:
        """Generate technical documentation with specifications - Unicode safe"""
        if not FPDF_AVAILABLE:
            print(f"⚠️ Skipping {product_name} docs - fpdf2 not available")
            return ""
        
        class TechnicalPDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 15)
                self.cell(0, 10, f'{product_name} Technical Specifications', new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
                self.ln(5)

        # Generate technical data
        specs = {
            'dimensions': f"{random.uniform(10, 50):.1f} x {random.uniform(10, 50):.1f} x {random.uniform(5, 20):.1f} cm",
            'weight': f"{random.uniform(0.5, 10):.1f} kg",
            'power_consumption': f"{random.uniform(50, 500):.0f} watts",
            'operating_temperature': f"{random.uniform(-10, 50):.0f}C to {random.uniform(60, 85):.0f}C",
            'efficiency': f"{random.uniform(85, 98):.1f}%",
            'processing_speed': f"{random.uniform(1, 10):.1f} GHz",
            'memory': f"{random.randint(4, 64)} GB",
            'storage': f"{random.randint(128, 2048)} GB",
        }
        
        # Performance benchmarks
        benchmarks = {
            'performance_test_1': random.uniform(90, 99),
            'reliability_test': random.uniform(85, 95),
            'stress_test': random.uniform(80, 90),
            'reliability_score': random.uniform(95, 99.9)
        }
        
        pdf = TechnicalPDF()
        pdf.add_page()
        
        # Technical Specifications
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Product Specifications', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        
        for spec, value in specs.items():
            pdf.cell(0, 8, f'{spec.replace("_", " ").title()}: {value}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Performance Data
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Performance Benchmarks', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        
        for test, score in benchmarks.items():
            pdf.cell(0, 8, f'{test.replace("_", " ").title()}: {score:.2f}%', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Technical Analysis with plain text
        pdf.ln(10)
        tech_analysis = f"""
Engineering Analysis:
The {product_name} demonstrates exceptional performance characteristics with 
a reliability score of {benchmarks['reliability_score']:.2f}%. Laboratory testing 
indicates optimal performance within specified operational parameters.

Quality Metrics:
- Mean Time Between Failures (MTBF): {random.randint(10000, 50000)} hours
- Quality Assurance Score: {random.uniform(95, 99):.1f}%
- Manufacturing Tolerance: +/-{random.uniform(0.1, 1.0):.2f}%
- Environmental Compliance: ISO 14001, RoHS, CE

Technical Recommendations:
For optimal performance, maintain operating conditions within specified ranges.
Regular calibration intervals of {random.randint(6, 24)} months are recommended.

Safety Standards:
- IEC 61010-1 compliance
- UL Listed components
- CE marking conformity
- FCC Part 15 Class B certified
        """
        
        pdf.multi_cell(0, 6, tech_analysis.strip())
        
        filename = f"{product_name.replace(' ', '_')}_technical_specs.pdf"
        filepath = self.output_dir / "technical_docs" / filename
        pdf.output(str(filepath))
        
        return str(filepath)

    def generate_research_paper_with_data(self, title: str, domain: str = "Computer Science") -> str:
        """Generate synthetic research paper with experimental data - Unicode safe"""
        if not FPDF_AVAILABLE:
            print(f"⚠️ Skipping research paper - fpdf2 not available")
            return ""
        
        class ResearchPDF(FPDF):
            def header(self):
                self.set_font('Helvetica', 'B', 12)
                self.multi_cell(0, 8, title, align='C')
                self.ln(5)

        # Generate experimental data
        methods = ['Proposed Method', 'Baseline A', 'Baseline B', 'State-of-Art']
        accuracy_scores = [random.uniform(0.85, 0.95), random.uniform(0.70, 0.80), 
                          random.uniform(0.75, 0.85), random.uniform(0.80, 0.90)]
        precision_scores = [random.uniform(0.82, 0.92), random.uniform(0.68, 0.78),
                           random.uniform(0.72, 0.82), random.uniform(0.78, 0.88)]
        recall_scores = [random.uniform(0.80, 0.90), random.uniform(0.65, 0.75),
                        random.uniform(0.70, 0.80), random.uniform(0.75, 0.85)]
        
        pdf = ResearchPDF()
        pdf.add_page()
        
        # Abstract
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Abstract', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        
        abstract = f"""
This paper presents a novel approach in {domain.lower()} addressing current limitations 
in the field. Our methodology achieves significant improvements over existing baselines, 
with accuracy improvements of up to {max(accuracy_scores)*100:.1f}%. The experimental 
evaluation demonstrates the effectiveness of our approach across multiple datasets 
and evaluation metrics. We introduce innovative techniques that outperform 
state-of-the-art methods by {((max(accuracy_scores) - min(accuracy_scores[1:]))*100):.1f} percentage points.
        """
        pdf.multi_cell(0, 5, abstract.strip())
        
        # Methodology
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Methodology', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        
        methodology = f"""
Our approach incorporates advanced techniques including data preprocessing, 
feature engineering, and model optimization. The experimental setup involves 
{random.randint(3, 10)} different datasets with {random.randint(1000, 50000)} samples each.

Model Parameters:
- Learning rate: {random.uniform(0.001, 0.1):.4f}
- Batch size: {random.choice([16, 32, 64, 128])}
- Hidden dimensions: {random.choice([256, 512, 1024])}
- Training epochs: {random.randint(50, 200)}
- Optimizer: {random.choice(['Adam', 'SGD', 'AdamW'])}
- Regularization: L2 with lambda = {random.uniform(0.0001, 0.01):.4f}

Dataset Information:
- Training samples: {random.randint(10000, 100000)}
- Validation samples: {random.randint(2000, 20000)}
- Test samples: {random.randint(2000, 20000)}
- Cross-validation: {random.randint(5, 10)}-fold
        """
        pdf.multi_cell(0, 5, methodology.strip())
        
        # Results
        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 10, 'Experimental Results', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 10)
        
        # Performance table
        for i, method in enumerate(methods):
            pdf.cell(0, 6, f'{method}: Acc={accuracy_scores[i]:.3f}, Prec={precision_scores[i]:.3f}, Rec={recall_scores[i]:.3f}', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # Statistical analysis
        pdf.ln(5)
        if DATA_VIZ_AVAILABLE:
            mean_acc = np.mean(accuracy_scores)
            std_acc = np.std(accuracy_scores)
        else:
            mean_acc = sum(accuracy_scores) / len(accuracy_scores)
            std_acc = (sum([(x - mean_acc)**2 for x in accuracy_scores]) / len(accuracy_scores))**0.5
        
        results_text = f"""
Statistical Analysis:
- Mean accuracy across methods: {mean_acc:.3f} +/- {std_acc:.3f}
- Best performing method: {methods[accuracy_scores.index(max(accuracy_scores))]} 
- Significance test (p-value): {random.uniform(0.001, 0.05):.4f}
- Effect size (Cohen's d): {random.uniform(0.5, 2.0):.2f}
- Confidence interval (95%): [{mean_acc-1.96*std_acc:.3f}, {mean_acc+1.96*std_acc:.3f}]

The results demonstrate statistically significant improvements over baseline methods,
with our proposed approach achieving state-of-the-art performance on benchmark datasets.
The improvements are consistent across different evaluation metrics and dataset splits.

Computational Efficiency:
- Training time: {random.uniform(0.5, 10):.1f} hours
- Inference time: {random.uniform(1, 100):.1f} ms per sample
- Memory usage: {random.uniform(2, 16):.1f} GB
- Model parameters: {random.uniform(1, 100):.1f}M
        """
        
        pdf.multi_cell(0, 5, results_text.strip())
        
        filename = f"research_{title.replace(' ', '_')[:30]}.pdf"
        filepath = self.output_dir / "research_papers" / filename
        pdf.output(str(filepath))
        
        return str(filepath)

    def populate_dataset(self):
        """Main method to populate the entire dataset"""
        print("🚀 Starting dataset population...")
        print(f"📦 Available packages: FPDF={FPDF_AVAILABLE}, DataViz={DATA_VIZ_AVAILABLE}, ArXiv={ARXIV_AVAILABLE}")
        
        generated_files = []
        
        # Download research papers if arxiv is available
        if ARXIV_AVAILABLE:
            try:
                arxiv_papers = self.download_arxiv_papers("multimodal RAG systems", max_papers=3)
                generated_files.extend([p['filename'] for p in arxiv_papers])
            except Exception as e:
                print(f"⚠️ ArXiv download failed: {e}")
        
        # Generate business reports
        companies = ["TechCorp Solutions", "DataViz Analytics", "AI Innovations Inc", "Future Systems Ltd"]
        for company in companies:
            try:
                filepath = self.generate_synthetic_business_report(company, 2024)
                if filepath:
                    generated_files.append(filepath)
                    print(f"📊 Generated business report: {company}")
            except Exception as e:
                print(f"⚠️ Error generating report for {company}: {e}")
        
        # Generate technical documentation
        products = ["Smart Analytics Platform", "Data Processing Engine", "Visualization Toolkit", "ML Pipeline System"]
        for product in products:
            try:
                filepath = self.generate_technical_documentation(product)
                if filepath:
                    generated_files.append(filepath)
                    print(f"⚙️ Generated technical docs: {product}")
            except Exception as e:
                print(f"⚠️ Error generating docs for {product}: {e}")
        
        # Generate research papers
        research_topics = [
            "Advanced RAG Systems with Multi-Agent Architectures",
            "Data Visualization in Information Retrieval", 
            "Agentic Approaches to Document Analysis",
            "Multimodal Document Understanding"
        ]
        for topic in research_topics:
            try:
                filepath = self.generate_research_paper_with_data(topic)
                if filepath:
                    generated_files.append(filepath)
                    print(f"📚 Generated research paper: {topic}")
            except Exception as e:
                print(f"⚠️ Error generating paper for {topic}: {e}")
        
        # Create summary
        summary = {
            'total_files': len(generated_files),
            'files_by_category': {
                'research_papers': len([f for f in generated_files if 'research_papers' in str(f)]),
                'business_reports': len([f for f in generated_files if 'business_reports' in str(f)]),
                'technical_docs': len([f for f in generated_files if 'technical_docs' in str(f)])
            },
            'generated_files': [str(f) for f in generated_files],
            'generation_date': datetime.now().isoformat(),
            'packages_used': {
                'fpdf2': FPDF_AVAILABLE,
                'data_visualization': DATA_VIZ_AVAILABLE,
                'arxiv': ARXIV_AVAILABLE
            }
        }
        
        with open(self.output_dir / "dataset_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n✅ Dataset population complete!")
        print(f"📁 Total files generated: {len(generated_files)}")
        print(f"📂 Output directory: {self.output_dir}")
        print(f"📄 Summary saved to: {self.output_dir}/dataset_summary.json")
        
        return summary

def main():
    """Main execution function"""
    print("📚 RAG Dataset Populator (Unicode Fixed Version)")
    print("=" * 60)
    
    # Create populator and run
    populator = RAGDatasetPopulator("rag_dataset")
    summary = populator.populate_dataset()
    
    print("\n🎯 Dataset Ready for RAG System!")
    print("📝 Usage Instructions:")
    print("1. Use the generated PDFs with your RAG system")
    print("2. Business reports contain financial data for visualization")  
    print("3. Technical docs have specifications and measurements")
    print("4. Research papers include experimental data and results")
    
    if summary['files_by_category']['business_reports'] > 0:
        print("\n💻 Example RAG CLI usage:")
        print("python cli.py process rag_dataset/business_reports/TechCorp_Solutions_annual_report_2024.pdf")
        print("python cli.py ask -f TechCorp_Solutions_annual_report_2024.pdf -q 'What was the quarterly revenue?' --agentic --visualize")
    
    print(f"\n📊 Generated Files Summary:")
    for category, count in summary['files_by_category'].items():
        print(f"   - {category.replace('_', ' ').title()}: {count} files")

if __name__ == "__main__":
    main()
