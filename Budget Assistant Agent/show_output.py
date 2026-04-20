with open('./analysis_output.txt', 'r') as f:
    content = f.read()

lines = content.split('\n')
print(f"Total lines: {len(lines)}")
print(f"Total characters: {len(content)}")
print("\n" + "="*100)
print("BEGINNING OF ANALYSIS:")
print("="*100)
for i, line in enumerate(lines[:60]):
    print(line)

print("\n\n" + "="*100)
print("END OF ANALYSIS:")
print("="*100)
for line in lines[-40:]:
    print(line)
