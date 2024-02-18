def format_trimestre(trimestre):
    year, quarter = trimestre.split("Q")
    quarter_labels = {'1': 'Ene-Mar', '2': 'Abr-Jun', '3': 'Jul-Sep', '4': 'Oct-Dic'}
    formatted_quarter = quarter_labels[quarter]
    return f"{formatted_quarter}/{year[2:]}"
