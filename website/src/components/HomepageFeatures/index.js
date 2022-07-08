import React from 'react';
import clsx from 'clsx';
import styles from './styles.module.css';

const FeatureList = [
  {
    title: 'Feature Rich',
    Svg: require('@site/static/img/feature_rich.svg').default,
    description: (
      <>
        <code>Core-Lib</code> supplies a variety of utility functions, with its support, we can accelerate development.
      </>
    ),
  },
  {
    title: 'Easy to Use',
    Svg: require('@site/static/img/easy_to_use.svg').default,
    description: (
      <>
        With its feature-rich design, <code>Core-Lib</code> is meant to make it simple to create and deploy applications.
      </>
    ),
  },
  {
    title: 'Get going quickly',
    Svg: require('@site/static/img/quick.svg').default,
    description: (
      <>
       With <code>Core-Lib</code> build apps in a jiffy and with ease.
      </>
    ),
  },
];

function Feature({Svg, title, description}) {
  return (
    <div className={clsx('col col--4')}>
      <div className="text--center">
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className="text--center padding-horiz--md">
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures() {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
