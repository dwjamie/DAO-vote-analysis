import requests
import json
import time
import tqdm


# Constants
GRAPHQL_ENDPOINT = "https://hub.snapshot.org/graphql"
HEADERS = {'Content-Type': 'application/json'}

# Define GraphQL Queries
proposals_query = """
query GetProposals($space: String!) {
  proposals(
    first: 1000,
    where: {
      space_in: [$space],
      state: "closed"
    },
    orderBy: "created",
    orderDirection: desc
  ) {
    id
    title
    choices
    scores
  }
}
"""

votes_query = """
query GetVotes($proposal: String!) {
  votes(
    first: 1000,
    where: {
      proposal: $proposal
    }
  ) {
    voter
    choice
    vp
    proposal {
      id
      title
      choices
    }
  }
}
"""

# Function to Run GraphQL Queries
def run_query(query, variables):
    request = requests.post(GRAPHQL_ENDPOINT, json={'query': query, 'variables': variables}, headers=HEADERS)
    time.sleep(0.75)
    if request.status_code == 200:
        return request.json()['data']
    else:
        raise Exception("Query failed with status code {}".format(request.status_code))

# Fetch Proposals
def get_proposals(space):
    proposals = run_query(proposals_query, {'space': space})['proposals']
    for proposal in proposals:
        max_score = max(proposal['scores'])
        proposal['winning'] = proposal['scores'].index(max_score) + 1
    return proposals

# Fetch Votes
def get_votes(proposal_id, proposals):
    votes = run_query(votes_query, {'proposal': proposal_id})['votes']
    for vote in votes:
        proposal_id = vote['proposal']['id']
        for proposal in proposals:
            if proposal['id'] == proposal_id:
                if vote['choice'] == proposal['winning']:
                    vote['result'] = 1
                    vote['win_contribution'] = vote['vp'] / proposal['scores'][vote['choice'] - 1]
                else:
                    vote['result'] = 0
                    vote['win_contribution'] = 0
                break
    return votes

# Function to Analyze a Single Voter
def analyze_voter(voter_id, votes):
    voter_info = {
        'vote_count': 0,
        'total_vp': 0,
        'avg_vp': 0,
        'win_rate': 0,
        'voted_proposals': []
    }

    win_count = 0
    for vote in votes:
        if vote['voter'] == voter_id:
            voter_info['vote_count'] += 1
            voter_info['total_vp'] += vote['vp']
            if vote['result'] == 1:
                win_count += 1

            # Add proposal info to the voter info
            voter_info['voted_proposals'].append({
                'proposal_id': vote['proposal']['id'],
                'title': vote['proposal']['title'],
                'choices': vote['proposal']['choices'],
                'voter_choice': vote['choice']
            })

    if voter_info['vote_count'] > 0:
        voter_info['avg_vp'] = voter_info['total_vp'] / voter_info['vote_count']
        voter_info['win_rate'] = win_count / voter_info['vote_count']

    return voter_info

# Main Analysis Function
def analyze_space(space):
    proposals = get_proposals(space)
    all_votes = []

    # Collect all votes from all proposals
    for proposal in proposals:
        votes = get_votes(proposal['id'], proposals)
        all_votes.extend(votes)

    # Analyze each voter
    voters_analysis = {}
    for vote in all_votes:
        voter_id = vote['voter']
        if voter_id not in voters_analysis:
            voters_analysis[voter_id] = analyze_voter(voter_id, all_votes)

    return voters_analysis

if __name__ == '__main__':
	# Analyze Lido and Optimism Spaces
    lido_analysis = analyze_space('lido-snapshot.eth')
    optimism_analysis = analyze_space('opcollective.eth')

    # Write results to JSON files
    with open('data/lido_analysis.json', 'w') as file:
        json.dump(lido_analysis, file, indent=4)

    with open('data/optimism_analysis.json', 'w') as file:
        json.dump(optimism_analysis, file, indent=4)
