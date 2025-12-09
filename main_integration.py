"""
Main Integration Script for Football Club Optimization System

This script integrates all components to provide:
- Complete match analysis and team selection
- Player form predictions and risk assessment
- Recruitment recommendations with visual profiles
"""

import sys
import os
sys.path.append('/workspace')

from football_optimization_system import FootballOptimizationSystem, create_sample_players
from recruitment_visualizer import RecruitmentVisualizer
import json
import pandas as pd


def generate_comprehensive_report():
    """Generate a comprehensive report combining all system outputs"""
    
    print("⚽ FOOTBALL CLUB OPTIMIZATION SYSTEM ⚽")
    print("=" * 60)
    
    # Initialize system with sample players
    players = create_sample_players()
    system = FootballOptimizationSystem(players)
    
    # Define opponent analysis
    opponent_strengths = {
        'attack': 0.8,
        'midfield': 0.6,
        'defense': 0.7
    }
    
    opponent_weaknesses = {
        'defense': 0.7,      # Weak in defense
        'set_pieces': 0.6,   # Weak in set pieces
        'right_flank': 0.8   # Very weak on right flank
    }
    
    print("\n🔍 OPPONENT ANALYSIS:")
    print(f"  Strengths: {', '.join([f'{k}({v*100:.0f}%)' for k, v in opponent_strengths.items()])}")
    print(f"  Weaknesses: {', '.join([f'{k}({v*100:.0f}%)' for k, v in opponent_weaknesses.items()])}")
    
    # Generate match report
    print("\n📋 GENERATING MATCH REPORT...")
    match_report = system.generate_match_report(
        opponent_strengths=opponent_strengths,
        opponent_weaknesses=opponent_weaknesses,
        match_importance=0.8
    )
    
    print(f"\n🎯 RECOMMENDED FORMATION: {match_report['formation']}")
    
    print("\n🏆 STARTING XI:")
    for i, player_info in enumerate(match_report['team_selection']['starting_11'], 1):
        player = player_info['player']
        print(f"  {i:2d}. {player.name:<25} [{player.position}] - {player_info['role']:<15} (Fitness: {player_info['fitness_score']})")
    
    print("\n🔄 BENCH:")
    for i, player_info in enumerate(match_report['team_selection']['bench'], 1):
        player = player_info['player']
        print(f"  {i:2d}. {player.name:<25} [{player.position}] - Bench (Fitness: {player_info['fitness_score']})")
    
    print("\n⚔️ KEY TACTICAL DUELS:")
    for duel in match_report['key_duels']:
        print(f"  • {duel['recommendation']} (Priority: {duel['priority']})")
    
    print("\n📋 TACTICAL RECOMMENDATIONS:")
    for note in match_report['tactical_recommendations']:
        print(f"  • {note}")
    
    # Generate player form predictions
    print("\n📊 PLAYER FORM PREDICTIONS (Next 4 Weeks):")
    for player in players[:5]:  # Show for top 5 players
        form_assessment = system.player_analyzer.assess_current_form(player)
        print(f"\n  {player.name}:")
        print(f"    Current Form: {form_assessment['current_form']:.1f}, "
              f"Trend: {form_assessment['trend']}, "
              f"Injury Risk: {'High' if form_assessment['injury_risk'] > 0.3 else 'Low'}")
        print("    Predictions:")
        for pred in form_assessment['predictions']:
            print(f"      {pred['date']}: {pred['predicted_form']:.1f} "
                  f"(Risk: {pred['risk_level']})")
    
    # Generate recruitment report
    print("\n🎯 RECRUITMENT REPORT:")
    recruitment_report = system.generate_recruitment_report()
    
    print("\n📈 TOP RECRUITMENT TARGETS:")
    for i, prospect in enumerate(recruitment_report[:10], 1):  # Top 10 targets
        print(f"  {i:2d}. {prospect['name']:<25} [{prospect['position']}] - "
              f"Priority: {prospect['recruitment_priority']}")
        print(f"       Overall: {prospect['overall_rating']:>2d}, "
              f"Potential: {prospect['potential']:.1f}, "
              f"Compatibility: {prospect['compatibility_score']:.1f}")
        print(f"       Strengths: {', '.join(prospect['strengths'])}")
        print(f"       Weaknesses: {', '.join(prospect['weaknesses'])}")
    
    # Generate visual recruitment profiles
    print("\n🖼️ GENERATING VISUAL PROFILES...")
    visualizer = RecruitmentVisualizer()
    
    # Create visual profiles for top 5 recruitment targets
    top_targets = recruitment_report[:5]
    visualizer.create_multiple_profiles(top_targets)
    
    # Also create profiles for starting 11
    starting_players_data = []
    for player_info in match_report['team_selection']['starting_11']:
        player = player_info['player']
        # Get the full profile for this player from the recruitment report
        profile = next((p for p in recruitment_report if p['name'] == player.name), None)
        if profile:
            starting_players_data.append(profile)
    
    visualizer.create_multiple_profiles(starting_players_data)
    
    # Generate CSV reports for data analysis
    print("\n📄 GENERATING DATA EXPORTS...")
    
    # Export team selection
    team_data = []
    for i, player_info in enumerate(match_report['team_selection']['starting_11']):
        player = player_info['player']
        team_data.append({
            'Number': i+1,
            'Name': player.name,
            'Position': player.position,
            'Role': player_info['role'],
            'Fitness_Score': player_info['fitness_score'],
            'Overall_Rating': player.overall_rating,
            'Current_Form': player.form,
            'Injury_Risk': player.injury_risk
        })
    
    df_team = pd.DataFrame(team_data)
    df_team.to_csv('/workspace/team_selection.csv', index=False)
    print("  ✓ Team selection exported to team_selection.csv")
    
    # Export recruitment targets
    df_recruitment = pd.DataFrame([
        {
            'Name': p['name'],
            'Position': p['position'],
            'Age': p['age'],
            'Overall_Rating': p['overall_rating'],
            'Current_Form': p['current_form'],
            'Potential': p['potential'],
            'Compatibility_Score': p['compatibility_score'],
            'Recruitment_Priority': p['recruitment_priority'],
            'Strengths': ', '.join(p['strengths']),
            'Weaknesses': ', '.join(p['weaknesses'])
        } for p in recruitment_report
    ])
    df_recruitment.to_csv('/workspace/recruitment_targets.csv', index=False)
    print("  ✓ Recruitment targets exported to recruitment_targets.csv")
    
    # Export player risks
    df_risks = pd.DataFrame([
        {
            'Name': name,
            'Position': next((p.position for p in players if p.name == name), 'Unknown'),
            'Current_Form': data['form'],
            'Fitness_Level': data['fitness'],
            'Injury_Risk': data['injury_risk'],
            'Performance_Trend': data['trend']
        } for name, data in match_report['player_risks'].items()
    ])
    df_risks.to_csv('/workspace/player_risks.csv', index=False)
    print("  ✓ Player risks exported to player_risks.csv")
    
    print(f"\n✅ COMPREHENSIVE REPORT GENERATED SUCCESSFULLY!")
    print(f"📁 Files created in /workspace/:")
    print(f"   - team_selection.csv")
    print(f"   - recruitment_targets.csv")
    print(f"   - player_risks.csv")
    print(f"   - /recruitment_profiles/ (directory with visual profiles)")


def main():
    """Main execution function"""
    try:
        generate_comprehensive_report()
    except Exception as e:
        print(f"❌ Error occurred during execution: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()