
def log_title(message: str) -> str:
    total_length = 100
    padded_word = f" {message} "
    left_filler_length = round((total_length - len(padded_word)) / 2)
    right_filler_length = total_length - len(padded_word) - left_filler_length

    left_filler = "=" * left_filler_length
    right_filler = "=" * right_filler_length

    log_string = left_filler + padded_word.upper() + right_filler

    return log_string
