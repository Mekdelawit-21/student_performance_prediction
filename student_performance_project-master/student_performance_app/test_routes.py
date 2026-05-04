from app import app

with app.test_client() as client:
    # Test pass/fail prediction
    r = client.post('/predict_pass_fail', json={'study_hours': 5, 'prev_exam_score': 75, 'attendance': 0.85, 'assignment_score': 80})
    print('Pass/Fail Status:', r.status_code)
    print('Pass/Fail Response:', r.get_json())
    
    # Test score prediction
    r = client.post('/predict_score', json={'study_hours': 5, 'prev_exam_score': 75, 'attendance': 0.85, 'assignment_score': 80})
    print('\nScore Status:', r.status_code)
    print('Score Response:', r.get_json())
    
    # Test dropout prediction
    r = client.post('/predict_dropout', json={'study_hours': 15, 'prev_exam_score': 62.5, 'attendance': 0.75, 'assignment_score': 70})
    print('\nDropout Status:', r.status_code)
    print('Dropout Response:', r.get_json())
