import cv2
import torch

def sample_frames(video_path, num_frames=8):
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    idxs = [int(i*(total-1)/(num_frames-1)) for i in range(num_frames)]

    frames = []
    for i in idxs:
        cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ok, frame = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()

    return frames

def capping_vid(vid_txt_to_txt_bundle, video_path):
    if not video_path:
        raise ValueError("video_path is required")
    
    video_model, video_processor = vid_txt_to_txt_bundle
    
    frames = sample_frames(video_path)

    # prompt
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "video", "video": frames},
                {
                    "type": "text", 
                    "text": """
                        Classify this video into ONE of the following ecommerce categories:
                        1. Fashion
                        2. Beauty
                        3. Electronics
                        4. Home
                        5. Fitness
                        6. Food
                        7. Baby
                        8. Hobby
                        9. Pets
                        10. Gaming
                        11. Outdoor
                        12. Automotives
                        13. Other
                    """
                }
            ]
        }
    ]
    # prompt into its template
    prompt = video_processor.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # put prompt and frame together
    inputs = video_processor(
        text=[prompt],
        videos=[frames],
        return_tensors="pt"
    )
    inputs = inputs.to("cpu")

    # inference
    generated_ids = video_model.generate(
        **inputs,
        max_new_tokens=64
    )

    # decode
    output = video_processor.batch_decode(
        generated_ids,
        skip_special_tokens=True
    )[0]
    
    #return caption
    return output
