        # Print raw results in railway logs to see what model is outputting
        print("MODEL RAW RESULTS:", results)
        
        Top_result = results[0] if results else {"label": "unknown", "score": 0.0}
        Label = top_result.get("label", "").lower()
        Score = top_result.get("score", 0.0)
        
        # Temporary logic: agar score high hai ya label kuch aur hai toh check karte hain
        # MelodyMachine model ke labels check karne ke liye:
        Is_deepfake = label != "real" and label != "bonafide" # Jo bhi real na ho wo deepfake
