const BabelMinifyPlugin = require("babel-minify-webpack-plugin");
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');

module.exports = {
    mode: "production",
    entry: process.env.WEBPACK_ENTRY,
    output: {
        path: process.env.WEBPACK_OUTPUT,
        filename: `bundle_${process.env.BUNDLE_NAME}.js`
    },
    module: {
        rules: [
            {
                test: /\.js$/,
                exclude: /node_modules/,
                use: ["babel-loader"],
            },
            {
                test: /\.css$/,
                use: [
                     MiniCssExtractPlugin.loader,
                    {
                        loader: "css-loader",
                        options: {importLoaders: 1}
                    },
                    {
                        loader: "postcss-loader",
                        options: {
                            ident: "postcss",
                            plugins: (loader) => [
                                require('postcss-preset-env')({
                                    stage: 4,
                                    autoprefixer: {grid: true},
                                }),
                                require("css-mqpacker")
                            ]
                        }
                    }]
            },
            {
                test: /\.scss$/,
                use: [
                    MiniCssExtractPlugin.loader,
                    {
                        loader: "css-loader",
                        options: {importLoaders: 1}
                    },
                    {
                        loader: "postcss-loader",
                        options: {
                            ident: "postcss",
                            plugins: (loader) => [
                                require('postcss-preset-env')({
                                    stage: 4,
                                    autoprefixer: {grid: true},
                                }),
                                require("css-mqpacker")
                            ]
                        }
                    },
                    "sass-loader"
                ],
            }
        ]
    },
    plugins: [
        new BabelMinifyPlugin,

        new MiniCssExtractPlugin({
            filename: `bundle_${process.env.BUNDLE_NAME}.css`,
        }),

        new OptimizeCSSAssetsPlugin({
                minimize: false,
                assetNameRegExp: /\.css$/,
                cssProcessor: require('cssnano'),
                cssProcessorPluginOptions: {
                    preset: [
                        'advanced',
                        {
                            discardComments: {
                                removeAll: true
                            },
                            reduceIdents: false,
                            zindex: false
                        }
                        ],
                },
                canPrint: true
            }),
    ],
};
