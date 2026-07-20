def test_group_update_and_leaderboard(client, authenticated_user):
    """
    Tests updating a user's study group and checking that they appear 
    correctly inside the leaderboard payload with their corresponding rank.
    """
    # Join a specific group
    group_name = "A test group"

    update_response = client.post('/api/update_group', 
                            json={'group': group_name
                        })
    
    assert update_response.status_code == 200

    # Add study time so the user shows up on today's logs
    client.post('/api/save_study_time',
                json={'minutes': 50
            })

    # Pull the leaderboard API payload
    leaderboard_response = client.get(f'/api/leaderboard_data?group={group_name}')
    assert leaderboard_response.status_code == 200
    
    json_data = leaderboard_response.get_json()
    assert json_data['group_name'] == group_name
    assert len(json_data['leaderboard']) > 0
    assert json_data['rank'] == "#1" # Only user in group, should be #1