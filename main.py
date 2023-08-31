import random
import time


def main():
    words = ['python', 'java', 'ruby', 'javascript', 'php', 'swift']
    score = 0

    while True:
        word = random.choice(words)
        print(f'文字列をタイプしてください：{word}')
        start_time = time.time()
        user_input = input().strip().lower()
        end_time = time.time()
        if user_input == 'q':
            print('ゲームを終了します。')
            break
        elif user_input == word:
            elapsed_time = end_time - start_time
            score += len(word) / elapsed_time
            print(f'正解です！ 今回の得点は {score:.2f} 点です。')
        else:
            print('不正解です。')

        print("Hello, World!")

if __name__ == "__main__":
    main()