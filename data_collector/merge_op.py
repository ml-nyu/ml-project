import pandas as pd
df = pd.read_csv('../input/test_data_4_students.csv', header=0,na_values='?')
y = df.id.map(lambda x: '{:.0f}'.format(x))

df1 = pd.read_csv('../test_output/op.csv', header=0,na_values='?')
z = pd.concat([y, df1.applymap(str).bot], axis=1)
z.to_csv('../test_output/Submission.csv', columns = ['id','bot'], sep=',', encoding='utf-8', index = False)