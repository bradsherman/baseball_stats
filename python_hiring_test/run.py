"""Main script for generating output.csv."""
import pandas as pd
import numpy as np

"""
This function takes in the split and spits out a few
strings that we need for querying the data
"""
def get_selection_info(split, team):
    suffix = "Id"
    if team:
        suffix = "Team" + suffix

    if split == "vs RHP":
        side = "R"
        split_clause = "PitcherSide"
        subject_id_str = "Hitter" + suffix
    elif split == "vs LHP":
        side = "L"
        split_clause = "PitcherSide"
        subject_id_str = "Hitter" + suffix
    elif split == "vs RHH":
        side = "R"
        split_clause = "HitterSide"
        subject_id_str = "Pitcher" + suffix
    elif split == "vs LHH":
        side = "L"
        split_clause = "HitterSide"
        subject_id_str = "Pitcher" + suffix

    return (side, split_clause, subject_id_str)

"""
This function takes in a dataframe, groups it by a subject,
aggregates the necessary data, and prunes the number of 
plate appearances
"""
def group_and_prune(filtered, sbj, min):
    group = filtered.groupby(sbj, as_index=False)
    new_df = group.agg({
        'PA': sum, 
        'AB': sum,
        'H': sum,
        'TB': sum,
        'BB': sum,
        'HBP': sum,
        'SF': sum })
    r = new_df[new_df['PA'] >= min]
    return r

"""
This function calculates one of the four statistics and adds 
it back to the dataframe passed in
"""
def calculate_stat(stat, df):
    if stat == 'AVG':
        avg = df.loc[:,'H'] / df.loc[:,'AB']
        df.loc[:,stat] = avg
    elif stat == 'OBP':
        # on base percentage is (H + BB + HBP) / (AB + BB + HBP + SF)
        obp_num = df.loc[:,'H'] + df.loc[:,'BB'] + df.loc[:,'HBP']
        obp_denom =  df.loc[:,'AB'] + df.loc[:,'BB'] + df.loc[:,'HBP'] + df.loc[:,'SF']
        df.loc[:,stat] = obp_num / obp_denom
    elif stat == 'SLG':
        # slugging percentage is TB / AB
        df.loc[:,stat] = df.loc[:,'TB'] / df.loc[:,'AB']
    elif stat == 'OPS':
        # on base + slugging is exactly that -> OBP + SLG 
        obp_num = df.loc[:,'H'] + df.loc[:,'BB'] + df.loc[:,'HBP']
        obp_denom =  df.loc[:,'AB'] + df.loc[:,'BB'] + df.loc[:,'HBP'] + df.loc[:,'SF']
        obp = obp_num / obp_denom
        slg = df.loc[:,'TB'] / df.loc[:,'AB']
        df.loc[:,stat] = obp + slg

    return df

"""
Main program logic
"""
def main():
    # define some constants
    min_PA = 25
    cols = ['SubjectId','Stat', 'Split', 'Subject', 'Value']
    infile = "./data/raw/pitchdata.csv"
    outfile = "./data/processed/output.csv"
    combinations_file = "./data/reference/combinations.txt"
    output = open(outfile, 'w')
    output.write(",".join(cols) + "\n")
    pitch_stats = pd.read_csv(infile)
    combos = pd.read_csv(combinations_file)

    # for each combination, let's crunch some data
    for _, combo in combos.iterrows():
        # define some constants that need to be redefined on each iteration
        team = False      # whether or not our subject is a team or player
        side = ""         # which side the player throws/hits 
        split_clause = "" # whether we are filtering pitcher or hitter's side

        """
        stat: (AVG, OBP, SLG, OPS)
        """
        stat = combo[0]
        """
        subject: (HitterId, HitterTeamId, PitcherId, PitcherTeamId)
        """
        subject = combo[1]
        # we need to know if we are dealing with a team
        if "Team" in subject:
            team = True
        """
        split: (vs LHH, vs LHP, vs RHH, vs RHP)
        """
        split = combo[2]
        
        # Get relevant information for selecting the data
        side, split_clause, subject_id_str = get_selection_info(split, team)

        # filter the dataset based on the split
        filtered_pitch_stats = pitch_stats[pitch_stats[split_clause] == side]

        # shrink our dataset to just the necessary information
        grouped_pitch_stats = group_and_prune(filtered_pitch_stats, subject, min_PA)

        # calculate our final dataset, and only keep the relevant information
        result_pitch_stats = calculate_stat(stat, grouped_pitch_stats)
        final_pitch_stats = result_pitch_stats[[subject, stat]]

        for item in final_pitch_stats.iterrows():
            # extract information from each row in the dataset
            sbj_id = item[1][subject_id_str]
            stat_value = item[1][stat]
            # construct output string
            out_string = str(int(sbj_id)) + "," + stat + "," + split + "," + \
                subject + "," + str(stat_value) + "\n"
            output.write(out_string)
        
    output.close()

    # read data back in and sort on the first four columns
    result_df = pd.read_csv(outfile)
    sorted_df = result_df.sort_values(cols[:-1])
    # round statistic values
    sorted_df['Value'] = sorted_df['Value'].round(3)
    # save back to the output file
    sorted_df.to_csv(outfile, index=False)


if __name__ == '__main__':
    main()
