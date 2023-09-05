import sqlite3
from pathlib import Path

DATABASE_FOLDER = Path("./assets/database").resolve()


def create_database(quiz_template):
    path = DATABASE_FOLDER / quiz_template.database_name
    if path.exists():
        print(f"{path} already exists.")
        return

    with sqlite3.connect(path) as conn:
        cursor = conn.cursor()

        # overview table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS overview (
            name TEXT,
            description TEXT
        )
        """
        )
        cursor.execute(
            "INSERT INTO overview (name, description) VALUES (?, ?)",
            (quiz_template.name, quiz_template.description),
        )

        # quizzes table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS quizzes (
            question TEXT PRIMARY KEY,
            answer TEXT,
            explanation TEXT
        )
        """
        )
        for question, answer, explanation in quiz_template.quizzes:
            cursor.execute(
                "INSERT INTO quizzes (question, answer, explanation) VALUES (?, ?, ?)",
                (question, answer, explanation),
            )

        # conn.commit()
        # conn.close()


class TestTyping:
    database_name = "test_typing.db"
    name = "タイピングテスト"
    description = "テスト用のタイピング文章"
    quizzes = [
        ("house", "house", "家を表す名詞"),
        ("Python", "Python", "インタープリンタ形式のプログラミング言語。機械学習の実装に向いている。"),
        ("apple", "apple", "りんごを表す名詞"),
        ("cat", "cat", "猫を表す名詞"),
        ("programming", "programming", "プログラミングをする行為"),
        ("dog", "dog", "犬を表す名詞"),
        ("book", "book", "本を表す名詞"),
        ("computer", "computer", "コンピュータを表す名詞"),
        ("tree", "tree", "木を表す名詞"),
        ("car", "car", "車を表す名詞"),
        ("python", "python", "爬虫類のヘビを表す名詞"),
        ("keyboard", "keyboard", "キーボードを表す名詞"),
        ("sky", "sky", "空を表す名詞"),
        ("flower", "flower", "花を表す名詞"),
        ("water", "water", "水を表す名詞"),
        ("moon", "moon", "月を表す名詞"),
        ("sun", "sun", "太陽を表す名詞"),
        ("earth", "earth", "地球を表す名詞"),
        ("phone", "phone", "電話を表す名詞"),
        ("music", "music", "音楽を表す名詞"),
    ]


class TestKanji:
    database_name = "test_kanji.db"
    name = "漢字の読みテスト"
    description = "テスト用の漢字の読み問題"
    quizzes = [
        ("胡椒", "こしょう", "つる性植物の果実を原料とする香辛料"),
        ("熟語", "じゅくご", "二字（以上）の漢字が結合して一語をなすもの"),
        ("形状", "けいじょう", "物の形や状態"),
        ("総合", "そうごう", "多くの要素をひとまとめに考慮すること"),
        ("自動", "じどう", "自ら動くこと"),
        ("方法", "ほうほう", "物事を行う手段や進め方"),
        ("基本", "きほん", "物事の根底となる考えや原則"),
        ("説明", "せつめい", "物事の意味や理由を明らかにすること"),
        ("雰囲気", "ふんいき", "その場その場の空気やムード"),
        ("計画", "けいかく", "未来の活動や行動を前もって考えること"),
        ("報告", "ほうこく", "情報や結果を他者に伝えること"),
        ("分析", "ぶんせき", "複雑な事象やデータを細部に分けて理解すること"),
        ("実験", "じっけん", "仮説や理論を確かめるための試み"),
        ("成功", "せいこう", "目的や計画がうまくいくこと"),
        ("失敗", "しっぱい", "目的や計画がうまくいかないこと"),
        ("動作", "どうさ", "物が動く仕組みや、人が動く行為"),
        ("参加", "さんか", "活動やイベントなどに加わること"),
        ("表現", "ひょうげん", "思いや感じを言葉、音、色、形などで示すこと"),
        ("関連", "かんれん", "二つ以上の事象や物が互いに影響を与える関係"),
        ("解答", "かいとう", "問題や疑問に対する答え"),
    ]


class TestKencho:
    database_name = "test_kencho.db"
    name = "県庁所在地はどこ？"
    description = "都道府県名から県庁所在地を答える問題"
    quizzes = [
        ("北海道", "札幌市\t札幌\tさっぽろし\tさっぽろ", ""),
        ("青森県", "青森市\t青森\tあおもりし\tあおもり", ""),
        ("岩手県", "盛岡市\t盛岡\tもりおかし\tもりおか", ""),
        ("宮城県", "仙台市\t仙台\tせんだいし\tせんだい", ""),
        ("秋田県", "秋田市\t秋田\tあきたし\tあきた", ""),
        ("山形県", "山形市\t山形\tやまがたし\tやまがた", ""),
        ("福島県", "福島市\t福島\tふくしまし\tふくしま", ""),
        ("茨城県", "水戸市\t水戸\tみとし\tみと", ""),
        ("栃木県", "宇都宮市\t宇都宮\tうつのみやし\tうつのみや", ""),
        ("群馬県", "前橋市\t前橋\tまえばしし\tまえばし", ""),
        ("埼玉県", "さいたま市\tさいたまし\tさいたま", ""),
        ("千葉県", "千葉市\t千葉\tちばし\tちば", ""),
        ("東京都", "新宿区\t新宿\tしんじゅくく\tしんじゅく\t東京\tとうきょう", ""),
        ("神奈川県", "横浜市\t横浜\tよこはまし\tよこはま", ""),
        ("新潟県", "新潟市\t新潟\tにいがたし\tにいがた", ""),
        ("富山県", "富山市\t富山\tとやまし\tとやま", ""),
        ("石川県", "金沢市\t金沢\tかなざわし\tかなざわ", ""),
        ("福井県", "福井市\t福井\tふくいし\tふくい", ""),
        ("山梨県", "甲府市\t甲府\tこうふし\tこうふ", ""),
        ("長野県", "長野市\t長野\tながのし\tながの", ""),
        ("岐阜県", "岐阜市\t岐阜\tぎふし\tぎふ", ""),
        ("静岡県", "静岡市\t静岡\tしずおかし\tしずおか", ""),
        ("愛知県", "名古屋市\t名古屋\tなごやし\tなごや", ""),
        ("三重県", "津市\t津\tつし\tつ", ""),
        ("滋賀県", "大津市\t大津\tおおつし\tおおつ", ""),
        ("京都府", "京都市\t京都\tきょうとし\tきょうと", ""),
        ("大阪府", "大阪市\t大阪\tおおさかし\tおおさか", ""),
        ("兵庫県", "神戸市\t神戸\tこうべし\tこうべ", ""),
        ("奈良県", "奈良市\t奈良\tならし\tなら", ""),
        ("和歌山県", "和歌山市\t和歌山\tわかやまし\tわかやま", ""),
        ("鳥取県", "鳥取市\t鳥取\tとっとりし\tとっとり", ""),
        ("島根県", "松江市\t松江\tまつえし\tまつえ", ""),
        ("岡山県", "岡山市\t岡山\tおかやまし\tおかやま", ""),
        ("広島県", "広島市\t広島\tひろしまし\tひろしま", ""),
        ("山口県", "山口市\t山口\tやまぐちし\tやまぐち", ""),
        ("徳島県", "徳島市\t徳島\tとくしまし\tとくしま", ""),
        ("香川県", "高松市\t高松\tたかまつし\tたかまつ", ""),
        ("愛媛県", "松山市\t松山\tまつやまし\tまつやま", ""),
        ("高知県", "高知市\t高知\tこうちし\tこうち", ""),
        ("福岡県", "福岡市\t福岡\tふくおかし\tふくおか", ""),
        ("佐賀県", "佐賀市\t佐賀\tさがし\tさが", ""),
        ("長崎県", "長崎市\t長崎\tながさきし\tながさき", ""),
        ("熊本県", "熊本市\t熊本\tくまもとし\tくまもと", ""),
        ("大分県", "大分市\t大分\tおおいたし\tおおいた", ""),
        ("宮崎県", "宮崎市\t宮崎\tみやざきし\tみやざき", ""),
        ("鹿児島県", "鹿児島市\t鹿児島\tかごしまし\tかごしま", ""),
        ("沖縄県", "那覇市\t那覇\tなはし\tなは", ""),
    ]


def main():
    create_database(TestTyping)
    create_database(TestKanji)
    create_database(TestKencho)


if __name__ == "__main__":
    main()
