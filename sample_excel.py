import xlsxwriter

# Create a new workbook
workbook = xlsxwriter.Workbook('sample_prospects.xlsx')

# Add a worksheet
worksheet = workbook.add_worksheet()

# Write headers
headers = ["Nom de l'entreprise", "Email", "Secteur", "Nombre d'employés", "Localisation", "Technologie", "Statut de contact"]
for col, header in enumerate(headers):
    worksheet.write(0, col, header)

# Write sample data
sample_data = [
    ["TechAI Solutions", "contact@techai-solutions.fr", "Intelligence Artificielle", 50, "Paris", "TensorFlow, PyTorch", "NotContacted"],
    ["Render3D Studio", "info@render3d-studio.fr", "Rendu 3D", 25, "Lyon", "Blender, Unreal Engine", "NotContacted"],
    ["VFX Pro", "hello@vfxpro.fr", "Effets Visuels", 30, "Bordeaux", "Maya, Nuke", "NotContacted"],
]

for row, data in enumerate(sample_data, start=1):
    for col, value in enumerate(data):
        worksheet.write(row, col, value)

# Close the workbook
workbook.close()

print("Sample Excel file 'sample_prospects.xlsx' created successfully!")