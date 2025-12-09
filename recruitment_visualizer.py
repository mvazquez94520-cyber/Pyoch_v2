"""
Recruitment Visualizer - Creates visual recruitment profiles for players

This module generates visual representations ("photo recrutement") of player profiles
that include key information in an easy-to-read format for coaches and scouts.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import font_manager
import numpy as np
import os
from datetime import datetime


class RecruitmentVisualizer:
    """Creates visual recruitment profiles for players"""
    
    def __init__(self, output_dir="/workspace/recruitment_profiles"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def create_player_profile_visual(self, player_data: dict):
        """
        Create a visual profile for a single player
        """
        # Create figure and axis
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # Set background color
        ax.set_facecolor('#f0f0f0')
        fig.patch.set_facecolor('#f0f0f0')
        
        # Title
        ax.text(0.5, 0.95, f"RECRUITMENT PROFILE: {player_data['name'].upper()}", 
                fontsize=20, ha='center', va='top', weight='bold', 
                transform=ax.transAxes, color='#2c3e50')
        
        # Position and Age
        ax.text(0.1, 0.88, f"Position: {player_data['position']}", 
                fontsize=14, ha='left', va='top', transform=ax.transAxes, 
                color='#34495e', weight='bold')
        ax.text(0.1, 0.85, f"Age: {player_data['age']}", 
                fontsize=14, ha='left', va='top', transform=ax.transAxes, 
                color='#34495e', weight='bold')
        
        # Overall Rating Circle
        circle_x, circle_y = 0.85, 0.86
        circle_radius = 0.06
        circle = patches.Circle((circle_x, circle_y), circle_radius, 
                               facecolor='#3498db', edgecolor='white', linewidth=3, 
                               transform=ax.transAxes)
        ax.add_patch(circle)
        ax.text(circle_x, circle_y, str(player_data['overall_rating']), 
                fontsize=20, ha='center', va='center', weight='bold', 
                transform=ax.transAxes, color='white')
        ax.text(circle_x, circle_y - 0.03, "OVERALL", 
                fontsize=9, ha='center', va='center', 
                transform=ax.transAxes, color='white')
        
        # Current Form Bar
        ax.text(0.1, 0.78, "CURRENT FORM:", 
                fontsize=12, ha='left', va='center', transform=ax.transAxes, 
                color='#2c3e50', weight='bold')
        form_bar_x_start = 0.25
        form_bar_width = 0.3
        form_normalized = player_data['current_form'] / 10.0  # Normalize to 0-1
        form_rect = patches.Rectangle((form_bar_x_start, 0.76), 
                                      form_bar_width * form_normalized, 0.03, 
                                      facecolor='#2ecc71', edgecolor='white', 
                                      transform=ax.transAxes)
        ax.add_patch(form_rect)
        # Empty bar outline
        empty_rect = patches.Rectangle((form_bar_x_start, 0.76), 
                                       form_bar_width, 0.03, 
                                       facecolor='none', edgecolor='#bdc3c7', 
                                       linewidth=1, transform=ax.transAxes)
        ax.add_patch(empty_rect)
        ax.text(0.4, 0.75, f"{player_data['current_form']:.1f}/10", 
                fontsize=10, ha='center', va='center', transform=ax.transAxes, 
                color='#2c3e50')
        
        # Fitness Level Bar
        ax.text(0.1, 0.71, "FITNESS LEVEL:", 
                fontsize=12, ha='left', va='center', transform=ax.transAxes, 
                color='#2c3e50', weight='bold')
        fitness_bar_x_start = 0.25
        fitness_bar_width = 0.3
        fitness_normalized = player_data['fitness_level'] / 10.0  # Normalize to 0-1
        fitness_rect = patches.Rectangle((fitness_bar_x_start, 0.69), 
                                         fitness_bar_width * fitness_normalized, 0.03, 
                                         facecolor='#3498db', edgecolor='white', 
                                         transform=ax.transAxes)
        ax.add_patch(fitness_rect)
        # Empty bar outline
        empty_rect = patches.Rectangle((fitness_bar_x_start, 0.69), 
                                       fitness_bar_width, 0.03, 
                                       facecolor='none', edgecolor='#bdc3c7', 
                                       linewidth=1, transform=ax.transAxes)
        ax.add_patch(empty_rect)
        ax.text(0.4, 0.68, f"{player_data['fitness_level']:.1f}/10", 
                fontsize=10, ha='center', va='center', transform=ax.transAxes, 
                color='#2c3e50')
        
        # Injury Risk Indicator
        ax.text(0.1, 0.64, "INJURY RISK:", 
                fontsize=12, ha='left', va='center', transform=ax.transAxes, 
                color='#2c3e50', weight='bold')
        risk_level = player_data['injury_risk']
        if risk_level < 0.2:
            risk_color = '#2ecc71'  # Green
            risk_text = "LOW"
        elif risk_level < 0.4:
            risk_color = '#f39c12'  # Orange
            risk_text = "MEDIUM"
        else:
            risk_color = '#e74c3c'  # Red
            risk_text = "HIGH"
        
        risk_circle = patches.Circle((0.25, 0.64), 0.02, 
                                    facecolor=risk_color, edgecolor='white', 
                                    linewidth=2, transform=ax.transAxes)
        ax.add_patch(risk_circle)
        ax.text(0.28, 0.64, risk_text, 
                fontsize=10, ha='left', va='center', transform=ax.transAxes, 
                color='#2c3e50', weight='bold')
        
        # Potential and Compatibility Scores
        pot_x, comp_x = 0.55, 0.75
        
        # Potential Score
        pot_circle = patches.Circle((pot_x, 0.64), 0.03, 
                                   facecolor='#9b59b6', edgecolor='white', 
                                   linewidth=2, transform=ax.transAxes)
        ax.add_patch(pot_circle)
        ax.text(pot_x, 0.64, f"{player_data['potential']:.1f}", 
                fontsize=12, ha='center', va='center', transform=ax.transAxes, 
                color='white', weight='bold')
        ax.text(pot_x, 0.61, "POTENTIAL", 
                fontsize=9, ha='center', va='center', 
                transform=ax.transAxes, color='#2c3e50')
        
        # Compatibility Score
        comp_circle = patches.Circle((comp_x, 0.64), 0.03, 
                                    facecolor='#e67e22', edgecolor='white', 
                                    linewidth=2, transform=ax.transAxes)
        ax.add_patch(comp_circle)
        ax.text(comp_x, 0.64, f"{player_data['compatibility_score']:.1f}", 
                fontsize=12, ha='center', va='center', transform=ax.transAxes, 
                color='white', weight='bold')
        ax.text(comp_x, 0.61, "COMPATIBILITY", 
                fontsize=9, ha='center', va='center', 
                transform=ax.transAxes, color='#2c3e50')
        
        # Strengths Section
        ax.text(0.1, 0.53, "STRENGTHS", 
                fontsize=14, ha='left', va='top', transform=ax.transAxes, 
                color='#27ae60', weight='bold')
        
        strengths = player_data['strengths']
        for i, strength in enumerate(strengths[:4]):  # Show max 4 strengths
            y_pos = 0.48 - i * 0.04
            strength_box = patches.Rectangle((0.1, y_pos - 0.015), 0.3, 0.03, 
                                            facecolor='#2ecc71', edgecolor='white', 
                                            transform=ax.transAxes, alpha=0.8)
            ax.add_patch(strength_box)
            ax.text(0.25, y_pos, strength.upper(), 
                    fontsize=10, ha='center', va='center', transform=ax.transAxes, 
                    color='white', weight='bold')
        
        # Weaknesses Section
        ax.text(0.55, 0.53, "WEAKNESSES", 
                fontsize=14, ha='left', va='top', transform=ax.transAxes, 
                color='#c0392b', weight='bold')
        
        weaknesses = player_data['weaknesses']
        for i, weakness in enumerate(weaknesses[:4]):  # Show max 4 weaknesses
            y_pos = 0.48 - i * 0.04
            weakness_box = patches.Rectangle((0.55, y_pos - 0.015), 0.35, 0.03, 
                                             facecolor='#e74c3c', edgecolor='white', 
                                             transform=ax.transAxes, alpha=0.8)
            ax.add_patch(weakness_box)
            ax.text(0.725, y_pos, weakness.upper(), 
                    fontsize=10, ha='center', va='center', transform=ax.transAxes, 
                    color='white', weight='bold')
        
        # Performance Trend
        trend_text = player_data['performance_trend']
        trend_color = '#2ecc71' if trend_text == 'Improving' else '#e74c3c' if trend_text == 'Declining' else '#f39c12'
        trend_symbol = '↗' if trend_text == 'Improving' else '↘' if trend_text == 'Declining' else '→'
        
        ax.text(0.1, 0.32, f"PERFORMANCE TREND: {trend_symbol} {trend_text.upper()}", 
                fontsize=12, ha='left', va='center', transform=ax.transAxes, 
                color=trend_color, weight='bold')
        
        # Recruitment Priority
        priority = player_data['recruitment_priority']
        priority_colors = {
            'High Priority': '#e74c3c',
            'Medium Priority': '#f39c12', 
            'Low Priority': '#3498db'
        }
        priority_color = priority_colors.get(priority, '#7f8c8d')
        
        priority_box = patches.Rectangle((0.6, 0.305), 0.3, 0.04, 
                                        facecolor=priority_color, edgecolor='white', 
                                        linewidth=2, transform=ax.transAxes)
        ax.add_patch(priority_box)
        ax.text(0.75, 0.325, priority.upper(), 
                fontsize=14, ha='center', va='center', transform=ax.transAxes, 
                color='white', weight='bold')
        
        # Footer
        current_date = datetime.now().strftime("%B %d, %Y")
        ax.text(0.5, 0.05, f"Generated on {current_date} | Recruitment Profile", 
                fontsize=10, ha='center', va='bottom', transform=ax.transAxes, 
                color='#7f8c8d', style='italic')
        
        # Remove axes
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        # Save the image
        filename = f"{self.output_dir}/{player_data['name'].replace(' ', '_')}_profile.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='#f0f0f0')
        plt.close()
        
        print(f"Created visual profile for {player_data['name']}: {filename}")
        return filename
    
    def create_multiple_profiles(self, players_data: list):
        """Create visual profiles for multiple players"""
        for player_data in players_data:
            self.create_player_profile_visual(player_data)


# Example usage function
def demo_visualization():
    """Demonstrate the visualization capabilities"""
    # Sample player data (this would normally come from the optimization system)
    sample_player = {
        'name': 'Mohamed Salah',
        'position': 'FWD',
        'age': 31,
        'overall_rating': 90,
        'current_form': 9.0,
        'fitness_level': 8.8,
        'injury_risk': 0.25,
        'motivation': 9.2,
        'performance_trend': 'Stable',
        'strengths': ['Shooting', 'Pace', 'Current Form', 'Goal Scoring'],
        'weaknesses': ['Defending'],
        'potential': 9.2,
        'compatibility_score': 9.1,
        'recruitment_priority': 'High Priority'
    }
    
    visualizer = RecruitmentVisualizer()
    visualizer.create_player_profile_visual(sample_player)
    
    print("Demo visualization created successfully!")


if __name__ == "__main__":
    demo_visualization()