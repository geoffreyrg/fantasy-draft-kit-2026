"""
Script to generate a realistic "Joel Smyth's Draft Guide 2026.pdf"
using reportlab with tabular player breakdowns, offensive line ratings,
luck regression indicators, and playcaller bellcow shares.
"""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_draft_guide_pdf(output_path: str):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'GuideTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1A365D"),
        alignment=1,
    )

    sub_style = ParagraphStyle(
        'GuideSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#4A5568"),
        alignment=1,
    )

    section_style = ParagraphStyle(
        'GuideSection',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=14,
        spaceAfter=6,
    )

    body_style = ParagraphStyle(
        'GuideBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#2D3748"),
    )

    # Header
    story.append(Paragraph("JOEL SMYTH'S FANTASY DRAFT GUIDE 2026", title_style))
    story.append(Paragraph("Context-Adjusted PPG, Luck Metrics, O-Line Ratings & Bellcow Volatility", sub_style))
    story.append(Spacer(1, 15))

    # Section 1: Player Analytical Cards (Adj PPG, Luck Lost, Unlucky Flag)
    story.append(Paragraph("1. Player Advanced Metrics & Luck Regression Index", section_style))
    story.append(Paragraph("Context-Adjusted PPG isolates playcalling, redzone efficiency regression, and injury discounts. Unlucky Flag indicates high TD positive regression.", body_style))
    story.append(Spacer(1, 8))

    player_headers = [
        "Player Name", "Pos", "Team", "2025 Raw PPG", "2025 Adj PPG",
        "Luck Pts Lost", "Unlucky Flag", "OL Run Rating", "RB1 Share %", "Pace Rank"
    ]

    players_data = [
        ["Ja'Marr Chase", "WR", "CIN", "21.4", "22.8", "24.5", "YES", "82.5", "18.0%", "4"],
        ["Bijan Robinson", "RB", "ATL", "18.6", "21.2", "31.2", "YES", "89.0", "78.5%", "7"],
        ["CeeDee Lamb", "WR", "DAL", "20.8", "21.5", "14.2", "NO", "84.2", "14.0%", "2"],
        ["Justin Jefferson", "WR", "MIN", "19.5", "21.0", "28.0", "YES", "79.0", "12.5%", "11"],
        ["Breece Hall", "RB", "NYJ", "17.8", "20.4", "26.4", "YES", "86.5", "74.0%", "9"],
        ["Amon-Ra St. Brown", "WR", "DET", "19.2", "19.8", "8.5", "NO", "94.5", "10.0%", "8"],
        ["Malik Nabers", "WR", "NYG", "16.8", "19.5", "22.0", "YES", "73.0", "15.0%", "15"],
        ["Saquon Barkley", "RB", "PHI", "19.8", "19.2", "-5.0", "NO", "96.0", "76.0%", "12"],
        ["Jahmyr Gibbs", "RB", "DET", "18.2", "19.0", "6.5", "NO", "94.5", "58.0%", "8"],
        ["Nico Collins", "WR", "HOU", "17.4", "18.9", "18.4", "YES", "80.5", "11.0%", "6"],
        ["Marvin Harrison Jr.", "WR", "ARI", "14.6", "17.8", "29.5", "YES", "78.0", "13.0%", "5"],
        ["Josh Allen", "QB", "BUF", "23.5", "23.8", "12.0", "NO", "85.0", "28.0%", "10"],
        ["Lamar Jackson", "QB", "BAL", "22.9", "23.2", "9.5", "NO", "88.0", "32.0%", "18"],
        ["Jayden Daniels", "QB", "WAS", "21.2", "22.5", "15.0", "YES", "76.5", "25.0%", "3"],
        ["Brock Bowers", "TE", "LV", "14.8", "16.5", "19.0", "YES", "74.0", "8.0%", "20"],
        ["Trey McBride", "TE", "ARI", "13.9", "15.8", "23.4", "YES", "78.0", "7.5%", "5"],
        ["De'Von Achane", "RB", "MIA", "16.5", "18.2", "14.8", "YES", "77.0", "62.0%", "1"],
        ["Kyren Williams", "RB", "LAR", "17.2", "16.8", "-8.2", "NO", "83.5", "72.0%", "14"],
        ["Garrett Wilson", "WR", "NYJ", "14.2", "17.2", "33.5", "YES", "86.5", "11.5%", "9"],
        ["Drake London", "WR", "ATL", "15.1", "17.0", "21.0", "YES", "89.0", "12.0%", "7"],
        ["Christian McCaffrey", "RB", "SF", "18.5", "19.5", "16.0", "YES", "91.0", "70.0%", "22"],
        ["Jonathan Taylor", "RB", "IND", "16.2", "17.5", "11.0", "NO", "87.5", "75.0%", "13"],
        ["Puka Nacua", "WR", "LAR", "16.0", "17.4", "15.5", "YES", "83.5", "9.0%", "14"],
        ["Brian Thomas Jr.", "WR", "JAX", "15.4", "17.1", "17.5", "YES", "75.0", "10.5%", "16"],
        ["Kenneth Walker III", "RB", "SEA", "14.8", "16.4", "18.0", "YES", "76.0", "65.0%", "17"],
        ["George Kittle", "TE", "SF", "13.5", "14.2", "5.0", "NO", "91.0", "6.0%", "22"],
        ["Sam LaPorta", "TE", "DET", "12.8", "14.0", "12.5", "YES", "94.5", "5.5%", "8"],
        ["Jalen Hurts", "QB", "PHI", "21.0", "21.5", "8.0", "NO", "96.0", "26.0%", "12"],
        ["Patrick Mahomes", "QB", "KC", "19.8", "21.8", "25.0", "YES", "87.0", "15.0%", "19"],
        ["Kyler Murray", "QB", "ARI", "19.5", "20.8", "17.0", "YES", "78.0", "22.0%", "5"],
        ["James Cook", "RB", "BUF", "15.0", "15.8", "10.0", "NO", "85.0", "60.0%", "10"],
        ["Derrick Henry", "RB", "BAL", "17.0", "16.2", "-12.0", "NO", "88.0", "68.0%", "18"],
        ["Tee Higgins", "WR", "CIN", "13.8", "16.0", "19.5", "YES", "82.5", "8.0%", "4"],
        ["Rashee Rice", "WR", "KC", "14.5", "16.8", "14.0", "YES", "87.0", "7.0%", "19"],
        ["Zay Flowers", "WR", "BAL", "13.2", "15.0", "11.0", "NO", "88.0", "9.0%", "18"],
        ["Tank Dell", "WR", "HOU", "12.8", "14.9", "16.0", "YES", "80.5", "8.0%", "6"],
        ["Chase Brown", "RB", "CIN", "13.5", "15.4", "14.2", "YES", "82.5", "64.0%", "4"],
        ["Jonathon Brooks", "RB", "CAR", "12.0", "15.0", "21.0", "YES", "79.5", "66.0%", "21"],
        ["Ladd McConkey", "WR", "LAC", "13.9", "15.8", "13.5", "YES", "81.0", "9.5%", "25"],
        ["Terry McLaurin", "WR", "WAS", "13.8", "15.5", "12.0", "NO", "76.5", "10.0%", "3"],
        ["Xavier Worthy", "WR", "KC", "11.8", "14.5", "20.5", "YES", "87.0", "8.5%", "19"],
        ["Dalton Kincaid", "TE", "BUF", "11.2", "13.8", "18.5", "YES", "85.0", "5.0%", "10"],
        ["Evan Engram", "TE", "JAX", "12.0", "13.2", "7.0", "NO", "75.0", "6.0%", "16"],
        ["David Montgomery", "RB", "DET", "14.0", "13.5", "-4.0", "NO", "94.5", "42.0%", "8"],
        ["Tony Pollard", "RB", "TEN", "13.2", "14.0", "9.0", "NO", "74.5", "63.0%", "24"],
        ["Najee Harris", "RB", "PIT", "13.0", "13.4", "4.0", "NO", "80.0", "56.0%", "28"],
        ["Chuba Hubbard", "RB", "CAR", "13.4", "13.8", "6.5", "NO", "79.5", "55.0%", "21"],
        ["Isiah Pacheco", "RB", "KC", "14.2", "15.0", "8.0", "NO", "87.0", "65.0%", "19"],
        ["Davante Adams", "WR", "NYJ", "13.5", "14.5", "15.0", "YES", "86.5", "8.0%", "9"],
        ["Rome Odunze", "WR", "CHI", "10.5", "14.2", "24.0", "YES", "78.5", "11.0%", "15"],
        ["Jaxon Smith-Njigba", "WR", "SEA", "12.4", "14.6", "16.8", "YES", "76.0", "9.0%", "17"],
        ["David Njoku", "TE", "CLE", "11.5", "12.8", "11.0", "NO", "77.5", "7.0%", "26"],
        ["Jake Ferguson", "TE", "DAL", "10.8", "12.4", "14.0", "YES", "84.2", "6.0%", "2"],
        ["Travis Kelce", "TE", "KC", "13.0", "13.2", "4.0", "NO", "87.0", "6.5%", "19"],
        ["Anthony Richardson", "QB", "IND", "18.0", "20.5", "22.0", "YES", "87.5", "24.0%", "13"],
        ["C.J. Stroud", "QB", "HOU", "18.5", "19.8", "14.5", "YES", "80.5", "12.0%", "6"],
        ["Joe Burrow", "QB", "CIN", "19.2", "20.4", "11.0", "NO", "82.5", "10.0%", "4"],
        ["Jordan Love", "QB", "GB", "18.2", "19.5", "13.0", "YES", "85.5", "14.0%", "16"],
        ["Baker Mayfield", "QB", "TB", "17.8", "18.5", "9.0", "NO", "81.0", "15.0%", "14"],
        ["Caleb Williams", "QB", "CHI", "16.5", "18.8", "19.0", "YES", "78.5", "18.0%", "15"]
    ]

    table_data = [player_headers] + players_data

    col_widths = [105, 28, 32, 60, 60, 60, 60, 62, 58, 48]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 4),
        ('TOPPADDING', (0, 0), (-1, 0), 4),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7.5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))

    story.append(t)
    story.append(Spacer(1, 15))

    # Section 2: Offensive Line & Playcaller Matrix
    story.append(Paragraph("2. Team Offensive Line Run-Block Grades & Pace Reference", section_style))
    story.append(Paragraph("Detailed trench metrics calibrated for 2026 offensive scheme shifts.", body_style))
    story.append(Spacer(1, 8))

    team_headers = ["Team", "OL Run Rating", "OL Pass Rating", "Neutral Pace Rank", "Bellcow RB1 Share", "Playcaller PROE"]
    team_data = [
        ["PHI", "96.0", "94.0", "12", "76.0%", "+2.5%"],
        ["DET", "94.5", "92.0", "8", "58.0%", "+1.8%"],
        ["SF",  "91.0", "86.5", "22", "70.0%", "-1.2%"],
        ["ATL", "89.0", "84.0", "7", "78.5%", "+3.2%"],
        ["BAL", "88.0", "82.5", "18", "68.0%", "-4.5%"],
        ["IND", "87.5", "85.0", "13", "75.0%", "+0.5%"],
        ["KC",  "87.0", "91.5", "19", "65.0%", "+6.8%"],
        ["NYJ", "86.5", "83.0", "9", "74.0%", "+1.5%"],
        ["GB",  "85.5", "88.0", "16", "55.0%", "+2.0%"],
        ["BUF", "85.0", "86.0", "10", "60.0%", "+3.0%"],
        ["DAL", "84.2", "85.0", "2", "52.0%", "+5.5%"],
        ["LAR", "83.5", "82.0", "14", "72.0%", "+0.8%"],
        ["CIN", "82.5", "84.5", "4", "64.0%", "+5.0%"],
        ["TB",  "81.0", "83.5", "14", "58.0%", "+2.8%"],
        ["LAC", "81.0", "80.5", "25", "62.0%", "-3.5%"],
        ["HOU", "80.5", "82.0", "6", "54.0%", "+4.2%"],
        ["PIT", "80.0", "76.0", "28", "56.0%", "-5.0%"],
        ["CAR", "79.5", "77.0", "21", "66.0%", "-1.5%"],
        ["MIN", "79.0", "81.5", "11", "52.0%", "+3.5%"],
        ["CHI", "78.5", "79.0", "15", "54.0%", "+1.0%"],
        ["ARI", "78.0", "76.5", "5", "58.0%", "+0.5%"],
        ["MIA", "77.0", "78.0", "1", "62.0%", "+4.0%"],
        ["WAS", "76.5", "75.0", "3", "50.0%", "+1.2%"],
        ["SEA", "76.0", "74.5", "17", "65.0%", "+0.0%"],
        ["JAX", "75.0", "75.5", "16", "55.0%", "+1.5%"],
        ["TEN", "74.5", "73.0", "24", "63.0%", "-2.0%"],
        ["LV",  "74.0", "73.5", "20", "52.0%", "-0.5%"],
        ["NYG", "73.0", "71.0", "15", "55.0%", "-1.0%"],
        ["DEN", "76.0", "75.0", "23", "50.0%", "-1.8%"],
        ["NE",  "72.0", "70.5", "27", "52.0%", "-3.0%"],
        ["NO",  "74.0", "75.0", "19", "54.0%", "+0.5%"],
        ["CLE", "77.5", "78.0", "26", "56.0%", "+0.0%"],
    ]

    t2 = Table([team_headers] + team_data, colWidths=[65, 85, 85, 95, 105, 95], repeatRows=1)
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t2)

    doc.build(story)
    print(f"Generated Joel Smyth Draft Guide PDF at: {output_path}")

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "raw" / "Joel Smyth's Draft Guide 2026.pdf"
    generate_draft_guide_pdf(str(out))
