### >> Presentation :
<br/>

![cropped and compressed logo](../img/cropped_and_compressed_logo.jpg)
<br/>
<br/>

The **bulb** package extends the **_Django_** framework to make it compatible with the **_Neo4j_** databases, and provides much more tools to deploy consequent websites.
Two other solutions already exist to use **Django** with **Neo4j**, but they each have their own inconveniences :  

| [**neo4django**](https://github.com/scholrly/neo4django) | [**neomodel**](https://github.com/neo4j-contrib/neomodel) |
|:--------------:|:------------:|
| This package is out of date (last update in 2013). His usage is deprecated, cause he runs under very old versions of all its components : _Python 2.X_ / _Django 1.5_ / _Neo4j 1.9_. Furthermore, **neo4django** does not provide support for the Django's sessions nor a complete support for the Django's authentication, nor a support for the Django administration. | This package is regularly updated, he runs also under last versions of all its components. He provides a very complete adaptation of the Django models, but the philosophy of these contributors is almost to make a 'ready and easy to use' tool, so the user interact only with the high-level surface. The inconvenience of a such reasoning, it's that you will have less freedom in what you want to do. This philosophy is perfect to deploy fastly some small projects, but it conduces to a total remake and to more complex programs the days where we will want to do more precise operations or we will want to improve the performances of our project, with creation of a cluster, for example. Furthermore, **neomodel** does not provides support for the Django's sessions nor for the Django's authentication and nor for the Django administration. |

**bulb** has a completely different philosophy. It offers you the choice to use "ready and easy to use" functions **to code fatser** or to let you interact with deeper concepts and to do exactly what you want to do. Firstly, the database interaction has been developed to let the user use writing queries and reading queries, but also more advanced concepts like make multi-transactions sessions and causal chaining. But on the other hand, methods have been developed to make easier the usage of these concepts.
> NB : The separation of writing and reading queries is the unique condition to set up clusters. So you you could just use these two 'ready to use' methods and get pretty good results.

Then, and to a lesser extent than **neomodel**, we have rewrite the Django's _'models'_ , to make them _'node_models'_. *bulb*'s node_models are a bit different than the original Django's models, but let you more flexibility. S

Look at this comparison chart, and make the better choice for your needs :

| | [**bulb**](https://github.com/LilaRest/bulb) | [**neomodel**](https://github.com/neo4j-contrib/neomodel) | [**neo4django**](https://github.com/scholrly/neo4django) |
|:--------------:|:------------:|:--------------:|:------------:|
| Python 2.X support | ❌ | ✅ | ✅ |
| Python 3.X support | ✅ | ✅ | ❌ |
| Last Neo4j versions support | ✅ | ✅ | ❌ |
| Last Django versions support | ✅ | ✅ | ❌ |
| Ready and easy to use models | ✅ | ✅ | ✅ |
| Highly customizable models | ✅ | ❌ | ❌ |
| Relationship directly integrated to models | ✅ | ✅ | ✅ |
| Independant and reusable relationship models | ✅ | ❌ | ❌ |
| Highly customizable relationship models | ✅ | ❌ | ❌ |
| Django's sessions support | ✅ | ❌ | ✅ |
| Django's authentication support | ✅ | ❌ | ✅ |
| Additional functionalities for authentication | ✅ | ❌ | ❌ |
| Django's administration support | ✅ | ❌ | ❌ |
| Highly customizable administration | ✅ | ❌ | ❌ |
| Neo4j's clusters support | ✅ | ❌ | ❌ |
| Neo4j's customizable sessions support | ✅ | ❌ | ❌ |
| Neo4j's causal chaining support | ✅ | ❌ | ❌ |
| Neo4j's geospacial operations support | ❌ | ✅ | ❌ |
| Fully CDN integration | ✅ | ❌ | ❌ |
| Automatic staticfiles compression | ✅ | ❌ | ❌ |
| Automatic staticfiles compilation | ✅ | ❌ | ❌ |
| Fully SFTP support for staticfiles | ✅ | ❌ | ❌ |
| Reinforcement of the password system | ✅ | ❌ | ❌ |
| SASS/SCSS support | ✅ | ❌ | ❌ |
| Webpack integration | ✅ | ❌ | ❌ |
| Polyfill integration | ✅ | ❌ | ❌ |
| Some front-end tools | ✅ | ❌ | ❌ |

To conclude, if you absolutely want exactly same models' structure than Django or if you have to make compatible an already existing project with Neo4j (and if you don't need neither sessions, nor authentication, nor administration), you should use [**neomodel**](https://github.com/neo4j-contrib/neomodel).
For the other cases, check this documentation :)

###### [>> Installation](https://bulb.readthedocs.io/en/latest/installation/)
<br/>
<br/>
<br/>
