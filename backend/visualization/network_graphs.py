import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Tuple
import numpy as np
import pandas as pd
import logging

class NetworkGraphGenerator:
    def __init__(self):
        self.color_palette = px.colors.qualitative.Set3
    
    def create_concept_network(self, concepts: List[Dict], relationships: List[Dict]) -> Dict:
        """Create a network graph of concept relationships"""
        try:
            # Create NetworkX graph
            G = nx.Graph()
            
            # Add nodes (concepts)
            for concept in concepts:
                G.add_node(
                    concept['concept_id'],
                    name=concept['name'],
                    subject=concept.get('subject', 'Unknown'),
                    frequency=concept.get('frequency', 1),
                    importance=concept.get('importance', 0.5)
                )
            
            # Add edges (relationships)
            for rel in relationships:
                if rel['concept_a'] in G.nodes and rel['concept_b'] in G.nodes:
                    G.add_edge(
                        rel['concept_a'],
                        rel['concept_b'],
                        weight=rel.get('strength', 0.5),
                        relationship_type=rel.get('relationship_type', 'related')
                    )
            
            # Generate layout
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Create Plotly traces
            edge_trace, node_trace = self._create_network_traces(G, pos)
            
            # Create figure
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Concept Relationship Network',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    annotations=[ dict(
                        text="Hover over nodes to see concept details",
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002,
                        xanchor='left', yanchor='bottom',
                        font=dict(color="#888", size=12)
                    )],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    template='plotly_white'
                )
            )
            
            # Generate insights
            insights = self._analyze_network_structure(G)
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "network",
                "network_stats": {
                    "total_concepts": G.number_of_nodes(),
                    "total_relationships": G.number_of_edges(),
                    "network_density": round(nx.density(G), 3),
                    "average_clustering": round(nx.average_clustering(G), 3)
                },
                "insights": insights
            }
            
        except Exception as e:
            logging.error(f"Error creating concept network: {str(e)}")
            return {"error": str(e)}
    
    def create_learning_path_network(self, learning_data: List[Dict]) -> Dict:
        """Create a learning path visualization"""
        try:
            # Create directed graph for learning progression
            G = nx.DiGraph()
            
            # Process learning data to create progression paths
            for session in learning_data:
                topics = session.get('topics_covered', [])
                timestamp = session.get('timestamp')
                
                # Add topics as nodes
                for topic in topics:
                    if not G.has_node(topic):
                        G.add_node(topic, first_learned=timestamp, frequency=0)
                    G.nodes[topic]['frequency'] += 1
                
                # Create edges for topic progression within session
                for i in range(len(topics) - 1):
                    source = topics[i]
                    target = topics[i + 1]
                    
                    if G.has_edge(source, target):
                        G[source][target]['weight'] += 1
                    else:
                        G.add_edge(source, target, weight=1)
            
            # Generate hierarchical layout
            pos = self._create_hierarchical_layout(G)
            
            # Create traces
            edge_trace, node_trace = self._create_directed_network_traces(G, pos)
            
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Learning Path Progression',
                    titlefont_size=16,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    template='plotly_white'
                )
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "learning_path",
                "path_stats": {
                    "total_topics": G.number_of_nodes(),
                    "learning_connections": G.number_of_edges(),
                    "learning_complexity": self._calculate_path_complexity(G)
                }
            }
            
        except Exception as e:
            logging.error(f"Error creating learning path network: {str(e)}")
            return {"error": str(e)}
    
    def create_document_similarity_network(self, documents: List[Dict], similarity_threshold: float = 0.3) -> Dict:
        """Create document similarity network"""
        try:
            G = nx.Graph()
            
            # Add document nodes
            for doc in documents:
                G.add_node(
                    doc['document_id'],
                    title=doc.get('filename', 'Unknown'),
                    subject=doc.get('subject', 'General'),
                    complexity=doc.get('complexity_score', 0.5),
                    size=doc.get('chunk_count', 10)
                )
            
            # Calculate similarity and add edges (simplified simulation)
            doc_ids = list(G.nodes())
            for i, doc_a in enumerate(doc_ids):
                for doc_b in doc_ids[i+1:]:
                    # Simulate similarity based on subject and complexity
                    subject_similarity = 1.0 if G.nodes[doc_a]['subject'] == G.nodes[doc_b]['subject'] else 0.3
                    complexity_similarity = 1.0 - abs(G.nodes[doc_a]['complexity'] - G.nodes[doc_b]['complexity'])
                    
                    similarity = (subject_similarity + complexity_similarity) / 2
                    
                    if similarity >= similarity_threshold:
                        G.add_edge(doc_a, doc_b, similarity=similarity)
            
            # Create layout
            pos = nx.spring_layout(G, k=2, iterations=50)
            
            # Create traces
            edge_trace, node_trace = self._create_document_network_traces(G, pos)
            
            fig = go.Figure(
                data=[edge_trace, node_trace],
                layout=go.Layout(
                    title='Document Similarity Network',
                    titlefont_size=16,
                    showlegend=True,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    template='plotly_white'
                )
            )
            
            return {
                "chart_data": fig.to_json(),
                "chart_type": "document_network",
                "similarity_stats": {
                    "total_documents": G.number_of_nodes(),
                    "similar_pairs": G.number_of_edges(),
                    "avg_similarity": round(np.mean([d['similarity'] for u, v, d in G.edges(data=True)]), 3) if G.edges() else 0
                }
            }
            
        except Exception as e:
            logging.error(f"Error creating document similarity network: {str(e)}")
            return {"error": str(e)}
    
    def _create_network_traces(self, G: nx.Graph, pos: Dict) -> Tuple[go.Scatter, go.Scatter]:
        """Create edge and node traces for network visualization"""
        # Edge trace
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            edge_data = G.get_edge_data(edge[0], edge[1])
            weight = edge_data.get('weight', 0.5)
            rel_type = edge_data.get('relationship_type', 'related')
            edge_info.append(f"Relationship: {rel_type}, Strength: {weight:.2f}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            name = node_data.get('name', node)
            subject = node_data.get('subject', 'Unknown')
            frequency = node_data.get('frequency', 1)
            importance = node_data.get('importance', 0.5)
            
            node_text.append(name)
            node_info.append(f"Concept: {name}<br>Subject: {subject}<br>Frequency: {frequency}<br>Importance: {importance:.2f}")
            
            # Color by subject
            subject_colors = {
                'Machine Learning': '#1f77b4',
                'Data Science': '#ff7f0e',
                'Mathematics': '#2ca02c',
                'Computer Science': '#d62728',
                'Physics': '#9467bd'
            }
            node_colors.append(subject_colors.get(subject, '#17becf'))
            
            # Size by importance/frequency
            node_sizes.append(max(10, frequency * 5 + importance * 20))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            hovertext=node_info,
            textposition="middle center",
            marker=dict(
                showscale=False,
                color=node_colors,
                size=node_sizes,
                line=dict(width=2, color='white')
            )
        )
        
        return edge_trace, node_trace
    
    def _create_directed_network_traces(self, G: nx.DiGraph, pos: Dict) -> Tuple[go.Scatter, go.Scatter]:
        """Create traces for directed network (learning paths)"""
        # Edge trace with arrows
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_sizes = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            frequency = node_data.get('frequency', 1)
            
            node_text.append(node[:15] + "..." if len(node) > 15 else node)
            node_info.append(f"Topic: {node}<br>Study frequency: {frequency}")
            node_sizes.append(max(15, frequency * 8))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            hovertext=node_info,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color='lightblue',
                line=dict(width=2, color='darkblue')
            )
        )
        
        return edge_trace, node_trace
    
    def _create_document_network_traces(self, G: nx.Graph, pos: Dict) -> Tuple[go.Scatter, go.Scatter]:
        """Create traces for document similarity network"""
        # Edge trace
        edge_x = []
        edge_y = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        node_sizes = []
        
        subject_colors = {
            'Machine Learning': '#1f77b4',
            'Data Science': '#ff7f0e',
            'Mathematics': '#2ca02c',
            'Computer Science': '#d62728',
            'Physics': '#9467bd',
            'General': '#17becf'
        }
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G.nodes[node]
            title = node_data.get('title', 'Unknown')
            subject = node_data.get('subject', 'General')
            complexity = node_data.get('complexity', 0.5)
            size = node_data.get('size', 10)
            
            short_title = title[:20] + "..." if len(title) > 20 else title
            node_text.append(short_title)
            node_info.append(f"Document: {title}<br>Subject: {subject}<br>Complexity: {complexity:.2f}")
            
            node_colors.append(subject_colors.get(subject, '#17becf'))
            node_sizes.append(max(15, size * 2))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            hovertext=node_info,
            textposition="middle center",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=1, color='white')
            )
        )
        
        return edge_trace, node_trace
    
    def _create_hierarchical_layout(self, G: nx.DiGraph) -> Dict:
        """Create hierarchical layout for directed graphs"""
        try:
            # Try to create a hierarchical layout
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Adjust y-coordinates based on node indegree (learning order)
            for node in G.nodes():
                indegree = G.in_degree(node)
                pos[node] = (pos[node][0], pos[node][1] + indegree * 0.5)
            
            return pos
        except:
            # Fallback to spring layout
            return nx.spring_layout(G)
    
    def _analyze_network_structure(self, G: nx.Graph) -> List[str]:
        """Analyze network structure and provide insights"""
        insights = []
        
        if G.number_of_nodes() == 0:
            return ["No concepts available for analysis"]
        
        # Network connectivity
        if nx.is_connected(G):
            insights.append("✅ All concepts are interconnected")
        else:
            components = nx.number_connected_components(G)
            insights.append(f"📊 Network has {components} separate concept groups")
        
        # Central concepts
        if G.number_of_nodes() > 1:
            centrality = nx.degree_centrality(G)
            central_node = max(centrality, key=centrality.get)
            central_name = G.nodes[central_node].get('name', central_node)
            insights.append(f"🎯 Most central concept: {central_name}")
        
        # Network density
        density = nx.density(G)
        if density > 0.5:
            insights.append("🔗 Highly interconnected knowledge network")
        elif density > 0.2:
            insights.append("📈 Moderately connected concepts")
        else:
            insights.append("🌱 Sparse concept connections - room for growth")
        
        return insights
    
    def _calculate_path_complexity(self, G: nx.DiGraph) -> float:
        """Calculate learning path complexity"""
        if G.number_of_nodes() <= 1:
            return 0.0
        
        # Average path length as complexity measure
        try:
            avg_path_length = nx.average_shortest_path_length(G)
            return min(avg_path_length / G.number_of_nodes(), 1.0)
        except:
            return 0.5  # Fallback for disconnected graphs
