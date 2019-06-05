#define _CRT_SECURE_NO_WARNINGS
#include "pch.h"
#include<iostream>
#include<stdio.h>
#include<stdlib.h>
#include<limits.h>
#include <cmath>
#include <algorithm>


#define N 50 //品物の数
#define LIMIT 60 //ナップサックの容量制限
#define POOLSIZE 50 //染色体の数(個体数)
#define LASTG 100 //繰り返しを打ち切る世代
#define MRATE 0.01 //突然変異が起こる確率
#define SEED 33

void initparcel(); //荷物の初期化
int evalfit(int gene[]); //適応度の計算
void mating(int pool[POOLSIZE][N], int ngpool[POOLSIZE * 2][N]); //交叉
void mutation(int ngpool[POOLSIZE * 2][N]); //突然変異
void printp(int pool[POOLSIZE][N]); //結果出力
void initpool(int pool[POOLSIZE][N]); //集団初期化
int rndn(int l); //n未満の乱数の生成
int rndn_one();//20%の確率で1を生成
int selectp(int roulette[POOLSIZE], int totalfitness); //親の選択
void crossing(int m[], int p[], int c1[], int c2[]); //特定の2染色体の交叉
void selectng(int ngpool[POOLSIZE * 2][N], int pool[POOLSIZE][N]); //次世代の選択

int parcel[N][2]; //荷物データ

int main(int argc, char *argv[]) {
	int pool[POOLSIZE][N];//染色体プール
	int ngpool[POOLSIZE * 2][N]; //次世代染色体プール
	int generation; //現在の世代数

	srand(SEED);

	rndn_one();
	initparcel(); //荷物データの読み込み
	initpool(pool); //集団の初期化

	for (generation = 0; generation < LASTG; ++generation) {
		printf("%d世代\n", generation);
		mating(pool, ngpool); //交叉
		mutation(ngpool); //突然変異
		selectng(ngpool, pool);//次世代の選択
		printp(pool); //結果出力
	}

	return 0;
}

/*荷物の初期化　データの読み取り*/
void initparcel() {
	FILE *fp;
	char fname[] = "data.txt";

	errno_t err;
	err = fopen_s(&fp, fname, "r");
	if (fp == NULL) {
		printf("%s file not open!\n", fname);
	}
	int i = 0;
	while ((i < N) && (fscanf_s(fp, "%d %d", &parcel[i][0], &parcel[i][1]) != EOF)) {
		++i;
	}

	fclose(fp);
}

/*集団の初期化*/
void initpool(int pool[POOLSIZE][N]) {
	for (int i = 0; i < POOLSIZE; ++i) {
		for (int j = 0; j < N; ++j) {
			pool[i][j] = rndn_one();
		}
	}
}

/*交叉*/
void mating(int pool[POOLSIZE][N], int ngpool[POOLSIZE * 2][N]) {
	int totalfitness = 0; //適応度の合計値
	int roulette[POOLSIZE];//適応度の格納
	int mama, papa; //親の遺伝子
	int i;

	if (rndn(100) / 100 < 30) {
		/*ルーレットの作成*/
		for (int i = 0; i < POOLSIZE; ++i) {
			roulette[i] = evalfit(pool[i]);
			/*適応度の合計値を計算*/
			totalfitness += roulette[i];
		}

		/*選択と交叉の繰り返し*/
		for (int i = 0; i < POOLSIZE; ++i) {
			do {
				/*親の選択*/
				mama = selectp(roulette, totalfitness);
				papa = selectp(roulette, totalfitness);
			} while (mama == papa);//重複の削除
			/*特定の2染色体の交叉*/
			crossing(pool[mama], pool[papa], ngpool[i * 2], ngpool[i * 2 + 1]);
		}
	}
}

/*突然変異*/
void mutation(int ngpool[POOLSIZE * 2][N]) {
	for (int i = 0; i < POOLSIZE * 2; ++i) {
		for (int j = 0; j < N; ++j) {
			if ((double)rndn(100) / 100.0 <= MRATE) {
				//反転させる
				if (ngpool[i][j] == 1)ngpool[i][j] = 0;
				else if (ngpool[i][j] == 0)ngpool[i][j] = 1;
			}
		}
	}
}

/*次世代の選択*/
void selectng(int ngpool[POOLSIZE * 2][N], int pool[POOLSIZE][N]) {
	int i, j, c;
	int totalfitness = 0; //適応度の合計値
	int roulette[POOLSIZE * 2]; //適応度の格納
	int ball; //選択位置の数値
	int acc = 0;

	/*選択を繰り返す*/
	for (i = 0; i < POOLSIZE; ++i) {
		/*ルーレットの作成*/
		totalfitness = 0;
		for (c = 0; c < POOLSIZE * 2; ++c) {
			roulette[c] = evalfit(ngpool[c]);
			totalfitness += roulette[c];//適応度の合計値を計算
		}
		/*染色体の一つを選ぶ*/
		ball = rndn(totalfitness);
		acc = 0;
		for (c = 0; c < POOLSIZE * 2; ++c) {
			acc += roulette[c];//適応度を積算
			if (acc > ball)break;//対応する遺伝子
		}
		/*染色体のコピー*/
		for (j = 0; j < N; ++j) {
			pool[i][j] = ngpool[c][j];
		}
	}
}

/*結果の出力*/
void printp(int pool[POOLSIZE][N]) {
	int fitness;//適応度
	double totalfitness = 0;//適応度の合計値
	int elite_num, bestfit = 0; //エリート遺伝子の処理用変数
	int i;
	int elite[N];//エリートを保存するため待避する配列

	for (int i = 0; i < POOLSIZE; ++i) {
		for (int j = 0; j < N; ++j) {
			printf("%1d", pool[i][j]);
		}
		fitness = evalfit(pool[i]);
		printf("\t%d\n", fitness);
		if (fitness > bestfit) {
			bestfit = fitness;
			elite_num = i;
		}
		totalfitness += fitness;
	}
	//elite_numにはこの世代で最も成績のよい個体の番号が入っているので，その遺伝子を，エリート配列に入れる
	for (i = 0; i < N; i++) {
		elite[i] = pool[elite_num][i];
	}
	for (i = 0; i < N; i++) {
		pool[0][i] = elite[i];
	}

	/*エリート解の適応度を出力*/
	printf("%d\t%d \t", elite, bestfit);
	/*平均の適応度を出力*/
	printf("%lf\n", totalfitness / POOLSIZE);
}

/*親の選択*/
int selectp(int roulette[POOLSIZE], int totalfitness) {
	int ball; //選択位置の制御
	int acc = 0; //適応度の積算値
	int i;
	ball = rndn(totalfitness);
	for (i = 0; i < POOLSIZE; ++i) {
		acc += roulette[i];
		if (acc > ball) {
			break;//対応する遺伝子
		}
	}
	return i;
}

/*特定の2染色体の交叉*/
void crossing(int m[], int p[], int c1[], int c2[]) {
	int j;
	int cp; //交叉する点

	/*交叉点の決定*/
	cp = rndn(N);

	/*前半部のコピー*/
	for (j = 0; j < cp; ++j) {
		c1[j] = m[j];
		c2[j] = p[j];
	}
	for (; j < N; ++j) {
		c2[j] = m[j];
		c1[j] = p[j];
	}
}
/*適応度の計算*/
int evalfit(int g[]) {
	int pos; //遺伝子座の指定
	int value = 0; //評価値
	int capa = 0; //容量

	/*各遺伝子座を調べて容量と評価値を計算*/
	for (pos = 0; pos < N; ++pos) {
		capa += parcel[pos][0] * g[pos];
		value += parcel[pos][1] * g[pos];
	}
	/*致死遺伝子の処理（容量制限を超えてしまった）*/
	if (capa >= LIMIT)value = 0;
	return value;
}
/*乱数*/
int rndn(int l) {
	int rndno;//生成した乱数
	while ((rndno = ((double)rand() / RAND_MAX)*l) == l);
	return rndno;
}

int rndn_one() {
	int ran;
	int l = 100;
	while ((ran = ((double)rand() / RAND_MAX)*l) == l);
	if (ran < 5) {
		return 1;
	}
	else {
		return 0;
	}
}

