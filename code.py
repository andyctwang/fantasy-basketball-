import pandas as pd


df = pd.read_csv('https://raw.githubusercontent.com/fantasydatapros/data/master/fantasypros/fp_projections.csv')
df = df.iloc[:, 1:]
', '.join(df.columns)
scoring_weights = {
    'receptions': 1, #PPR
    'receiving_yds': 0.1,
    'receiving_td': 6,
    'FL': -2, #fumble lost
    'rushing_yds': 0.1,
    'rushing_td': 6,
    'passing_yds': 0.04,
    'passing_td': 4,
    'int': -2
}

df['FantacyPoint'] = (
    df['Receptions']*scoring_weights['receptions'] + df['ReceivingYds']*scoring_weights['receiving_yds'] + \
    df['ReceivingTD']*scoring_weights['receiving_td'] + df['FL']*scoring_weights['FL'] + \
    df['RushingYds']*scoring_weights['rushing_yds'] + df['RushingTD']*scoring_weights['rushing_td'] + \
    df['PassingYds']*scoring_weights['passing_yds'] + df['PassingTD']*scoring_weights['passing_td'] + \
    df['Int']*scoring_weights['int'] )

base_columns = ['Player', 'Team', 'Pos']
rushing_columns = ['FantasyPoints', 'Receptions', 'ReceivingYds', 'ReceivingTD', 'RushingAtt', 'RushingYds', 'RushingTD', 'FL']
rb_df = df.loc[df['Pos'] == 'RB', base_columns + rushing_columns]
rb_df['RushingTDRank'] = rb_df['RushingAtt'].rank(ascending = False)

adp_df = pd.read_csv('https://raw.githubusercontent.com/fantasydatapros/data/master/fantasypros/adp/PPR_ADP.csv')
adp_df = adp_df.iloc[:, 1:]
adp_df['ADP RANK'] = adp_df['AVG'].rank()
adp_df_cutoff = adp_df[:100]
replacement_players = {
    'RB':'',
    'QB':'',
    'WR':'',
    'TE':''
}

for _, row in adp_df_cutoff.iterrows():
    position = row['POS']
    player = row['PLAYER']
    if position in replacement_players:
        replacement_players[position] = player

df = df[['Player', 'Pos', 'Team', 'FantasyPoints']]

replacement_values = {}
for position, player_name in replacement_players.items():
    player = df.loc[df['Player'] == player_name]
    replacement_values[position] = player['FantasyPoints'].tolist()[0]

df = df.loc[df['Pos'].isin(['QB', 'RB', 'WR', 'TE'])]

df['VOR'] = df.apply(
    lambda row: row['FantasyPoints'] - replacement_values.get(row['Pos']), axis = 1)
df['VOR Rank'] = df['VOR'].rank(ascending = False)

df = df.rename({
    'VOR': 'Value',
    'VOR Rank': 'Value Rank'
}, axis = 1)

adp_df = adp_df.rename({
    'PLAYER': 'Player',
    'POS': 'Pos',
    'AVG': 'Average ADP',
    'ADP RANK': 'ADP Rank'
}, axis = 1)

final_df = df.merge(adp_df, how = 'left', on = ['Player', 'Pos'])
final_df['Diff in ADP and Value'] = final_df['ADP Rank'] - final_df['Value Rank']

draft_pool = final_df.sort_values(by = 'ADP Rank')[:196]

rb_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'RB']
qb_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'QB']
wr_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'WR']
te_draft_pool = draft_pool.loc[draft_pool['Pos'] == 'TE']

# top 10 RB sleepers for this year's draft
print(rb_draft_pool.sort_values(by = 'Diff in ADP and Value', ascending = False)[:10])

# top 10 RB overvalued for this year's draft
print(rb_draft_pool.sort_values(by='Diff in ADP and Value', ascending = True)[:10])

# top 10 WR sleepers for this year's draft
print(wr_draft_pool.sort_values(by='Diff in ADP and Value', ascending = False)[:10])

# top 10 WR overvalued for this year's draft
print(wr_draft_pool.sort_values(by='Diff in ADP and Value', ascending = True)[:10])

# top 10 TE sleepers for this year's draft
print(te_draft_pool.sort_values(by='Diff in ADP and Value', ascending = False)[:10])

# top 10 TE overvalued for this year's draft
print(te_draft_pool.sort_values(by='Diff in ADP and Value', ascending = True)[:10])

# top 10 QB sleepers for this year's draft
print(qb_draft_pool.sort_values(by='Diff in ADP and Value', ascending = False)[:10])

# top 10 QB overvalued for this year's draft
print(qb_draft_pool.sort_values(by='Diff in ADP and Value', ascending = True)[:10])



