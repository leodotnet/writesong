from gradio_client import Client, handle_file

client = Client("http://127.0.0.1:7865/")
result = client.predict(
		format="mp3",
		audio_duration=-1,
		prompt="baby, pop, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, upbeat, groovy, cozy",
		lyrics="""[verse]
小鸭子，小鸭子，
嘎嘎嘎地叫。
一身黄黄的羽毛，
真可爱，真奇妙。

[chorus]
池塘边，水中央，
小鸭子乐悠悠。
摇摇摆摆划着水，
快乐又自由。

[verse]
小嘴巴，扁又扁，
水里找小虾。
尾巴摇啊摇啊摇，
玩得真开花。

[chorus]
池塘边，水中央，
小鸭子乐悠悠。
摇摇摆摆划着水，
快乐又自由。

[bridge]
太阳照，风儿吹，
小鸭子不怕累。
从小鸭子变大鸭，
勇敢向前追。

[chorus]
池塘边，水中央，
小鸭子乐悠悠。
摇摇摆摆划着水，
快乐又自由。
""",
		infer_step=60,
		guidance_scale=15,
		scheduler_type="euler",
		cfg_type="apg",
		omega_scale=10,
		manual_seeds=None,
		guidance_interval=0.5,
		guidance_interval_decay=0,
		min_guidance_scale=3,
		use_erg_tag=True,
		use_erg_lyric=False,
		use_erg_diffusion=True,
		oss_steps=None,
		guidance_scale_text=0,
		guidance_scale_lyric=0,
		audio2audio_enable=False,
		ref_audio_strength=0.5,
		ref_audio_input=None,
		lora_name_or_path="none",
		lora_weight=1,
		api_name="/__call__"
)
print(result)


# example result

example_result = ('/tmp/gradio/793331485d22fdc7ec17208172e168c5f7182bbe7910cac352fd4dbc89c34fba/output_20250713170455_0.wav', {'format': 'wav', 'lora_name_or_path': 'none', 'lora_weight': 1, 'task': 'text2music', 'prompt': 'funk, pop, soul, rock, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, energetic, upbeat, groovy, vibrant, dynamic', 'lyrics': "[verse]\nNeon lights they flicker bright\nCity hums in dead of night\nRhythms pulse through concrete veins\nLost in echoes of refrains\n\n[verse]\nBassline groovin' in my chest\nHeartbeats match the city's zest\nElectric whispers fill the air\nSynthesized dreams everywhere\n\n[chorus]\nTurn it up and let it flow\nFeel the fire let it grow\nIn this rhythm we belong\nHear the night sing out our song\n\n[verse]\nGuitar strings they start to weep\nWake the soul from silent sleep\nEvery note a story told\nIn this night we’re bold and gold\n\n[bridge]\nVoices blend in harmony\nLost in pure cacophony\nTimeless echoes timeless cries\nSoulful shouts beneath the skies\n\n[verse]\nKeyboard dances on the keys\nMelodies on evening breeze\nCatch the tune and hold it tight\nIn this moment we take flight\n", 'audio_duration': 163.5051567887207, 'infer_step': 60, 'guidance_scale': 15, 'scheduler_type': 'euler', 'cfg_type': 'apg', 'omega_scale': 10, 'guidance_interval': 0.5, 'guidance_interval_decay': 0, 'min_guidance_scale': 3, 'use_erg_tag': True, 'use_erg_lyric': False, 'use_erg_diffusion': True, 'oss_steps': [], 'timecosts': {'preprocess': 0.20573019981384277, 'diffusion': 13.698843479156494, 'latent2audio': 9.895848512649536}, 'actual_seeds': [1860512770], 'retake_seeds': [3424195672], 'retake_variance': 0.5, 'guidance_scale_text': 0, 'guidance_scale_lyric': 0, 'repaint_start': 0, 'repaint_end': 0, 'edit_n_min': 0.0, 'edit_n_max': 1.0, 'edit_n_avg': 1, 'src_audio_path': None, 'edit_target_prompt': None, 'edit_target_lyrics': None, 'audio2audio_enable': False, 'ref_audio_strength': 0.5, 'ref_audio_input': None, 'audio_path': './outputs/output_20250713170455_0.wav'})
